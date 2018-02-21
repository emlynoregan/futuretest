from flask import render_template#, request, redirect
from megatest import register_test
from taskutils.task import PermanentTaskFailure, task
import time
from taskutils.future import FutureReadyForResult, GetFutureAndCheckReady

def get_helloworld(app):
    @app.route('/hw', methods=["GET", "POST"])
    def helloworld():
        return render_template("helloworld.html")

@register_test
def firsttest(futurekey):
    pass

@register_test(tags=["fails"])
def secondtest(futurekey):
    raise PermanentTaskFailure("This test fails")


@register_test(description="This is a slow test...", tags=["fails"])
def slowtest(futurekey):
    time.sleep(20)
    return True

@register_test(description="Kicks off a task, which fires later and marks success", tags=["task"])
def slowtestusingtask(futurekey):
    @task(countdown=20)
    def SetResult():
        fut = GetFutureAndCheckReady(futurekey)
        fut.set_success(True)
        
    SetResult()
    raise FutureReadyForResult("waiting")

@register_test(description="slow with progress", tags=["task"])
def progresstest(futurekey):
    @task(countdown=1)
    def Tick(aProgress):
        fut = GetFutureAndCheckReady(futurekey)
        fut.set_localprogress(aProgress * 5)
        if aProgress < 20:
            Tick(aProgress+1)
        else:
            fut.set_success(aProgress)
        
    Tick(0)
    raise FutureReadyForResult("waiting")
