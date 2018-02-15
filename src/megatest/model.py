from google.appengine.ext import ndb
from taskutils.future import future
import uuid
from taskutils.debouncedtask import debouncedtask
import datetime
from megatest.util import DateTimeToUnixTimestampMicrosec

_TEST_RUN_STATUSES = ["pre", "underway", "pass", "fail"]
_TEST_RUN_STATUS_PRE = _TEST_RUN_STATUSES[0]
_TEST_RUN_STATUS_UNDERWAY = _TEST_RUN_STATUSES[1]
_TEST_RUN_STATUS_PASS = _TEST_RUN_STATUSES[2]
_TEST_RUN_STATUS_FAIL = _TEST_RUN_STATUSES[3]

class TestRun(ndb.model.Model):
    testname = ndb.StringProperty()
    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    started = ndb.DateTimeProperty()
    status = ndb.StringProperty()
    progress = ndb.FloatProperty()

    final_runtime_usec = ndb.IntegerProperty()
    final_message = ndb.StringProperty()
    
    futurekey = ndb.KeyProperty()
    
    @classmethod
    def construct_key(cls):
        lid = str(uuid.uuid4())
        return cls.construct_key_for_id(lid)

    @classmethod
    def construct_key_for_id(cls, aId):
        return ndb.Key(TestRun, aId)
        
    @classmethod
    def go(cls, testDef):
        lrunKey = cls.construct_key()
        
        lrun = TestRun(
            key = lrunKey,
            testname = testDef.get("name"),
            status = _TEST_RUN_STATUS_PRE,
            progress = 0,
            
        )

        ltaskkwargs = testDef.get("taskkwargs") or {}
        f = testDef.get("f")

        def calc_final_runtime_usec(aStarted):
            lnow = datetime.datetime.utcnow()
            
            return int(
                (lnow - aStarted).total_seconds() * 1000000
            )
             
        def onsuccess(futurekey):
            futureobj = futurekey.get() if futurekey else None
            if futureobj:
                lrun = lrunKey.get()
                
                if lrun and lrun.status in [_TEST_RUN_STATUS_PRE, _TEST_RUN_STATUS_UNDERWAY]:
                    lrun.status = _TEST_RUN_STATUS_PASS
                    lrun.progress = 100
                    lresult = futureobj.get_result()
                    if lresult:
                        lrun.final_message = str(lresult)
                    lrun.final_runtime_usec = calc_final_runtime_usec(lrun.started)
                    lrun.put()
        
        def onfailure(futurekey):
            futureobj = futurekey.get() if futurekey else None
            if futureobj:
                lrun = lrunKey.get()
                
                if lrun and lrun.status in [_TEST_RUN_STATUS_PRE, _TEST_RUN_STATUS_UNDERWAY]:
                    lrun.status = _TEST_RUN_STATUS_FAIL
                    lrun.progress = 100
                    try:
                        futureobj.get_result()
                    except Exception, ex:
                        lrun.final_message = str(ex)
                    lrun.final_runtime_usec = calc_final_runtime_usec(lrun.started)
                    lrun.put()

        @debouncedtask(**ltaskkwargs)
        def onprogress(futurekey):
            futureobj = futurekey.get() if futurekey else None
            if futureobj:
                lrun = lrunKey.get()
                if lrun and lrun.status in [_TEST_RUN_STATUS_PRE, _TEST_RUN_STATUS_UNDERWAY]:
                    lrun.progress = futureobj.get_calculatedprogress()
                    lrun.put()
        
        fut = future(
            f, 
            onsuccessf = onsuccess, 
            onfailuref = onfailure, 
            onprogressf = onprogress, 
            weight = 100,
            **ltaskkwargs
        )()

        lrun.futurekey = fut.key
        lrun.started = datetime.datetime.utcnow()
        lrun.put()
                
        return lrun

    def to_json(self):
        retval = {
            "id": self.key.id(),
            "testname": self.testname,
            "stored": DateTimeToUnixTimestampMicrosec(self.stored) if not self.stored is None else None,
            "stored_desc": self.stored,
            "updated": DateTimeToUnixTimestampMicrosec(self.updated) if not self.updated is None else None,
            "updated_desc": self.updated,
            "status": self.status
        }
        
        if self.status in [_TEST_RUN_STATUS_UNDERWAY, _TEST_RUN_STATUS_PASS, _TEST_RUN_STATUS_FAIL]:
            retval.update({
                "started": DateTimeToUnixTimestampMicrosec(self.started),
                "started_desc": self.started,
                "progress": self.progress,
                "futurekey": self.futurekey.urlsafe() if self.futurekey else None,
            })        

        if self.status in [_TEST_RUN_STATUS_PASS, _TEST_RUN_STATUS_FAIL]:
            retval.update({
                "final_runtime_usec": self.final_runtime_usec,
                "final_message": self.final_message
            })        
        
        return retval

    def cancel(self):
        if self.status in [_TEST_RUN_STATUS_UNDERWAY]:
            fut = self.futurekey.get if self.futurekey else None
            
            if fut:
                fut.cancel()
    
    