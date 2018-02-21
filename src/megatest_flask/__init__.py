from flask import render_template, request, jsonify, make_response
from megatest import get_test_by_name, get_tests, get_testrun_by_id,\
    get_testruns, run_test, cancel_test_run, delete_test_run,\
    get_json_testrun_by_id
import json
import logging
_base_route = "megatest"

def _create_route(suffix):
    global _base_route
    return "/%s/%s" % (_base_route, suffix)

def set_base_route(base_route):
    global _base_route
    _base_route = base_route

def register_tests_api(app):
    @app.route(_create_route("tests"), methods=["GET", "POST"])
    def tests_api():
        if request.method == "GET":
            ltestname = request.args.get('name')
            ltagsRaw = request.args.get('tags')
    
            retval = None
            if ltestname:
                retval = get_test_by_name(ltestname.strip())
            else:
                ltags = json.loads(ltagsRaw) if ltagsRaw else []
                retval = get_tests(ltags)
                
            return jsonify(retval)
        else: # POST
            lbodyJson = request.get_json()
            if not lbodyJson:
                return "json request required", 400
            
            laction = lbodyJson.get("action")
            if laction == "go":
                ltestname = lbodyJson.get("name")
                if not ltestname:
                    return "name field required", 400
                else:
                    ltest = get_test_by_name(ltestname)
                    if not ltest:
                        return "can't find test %s" % ltestname, 404
                    else:
                        ltestRun = run_test(ltestname)
                        return jsonify({
                            "id": ltestRun.key.id()
                        })
            else:
                return "unknown action %s" % laction, 400
    
    @app.route(_create_route("runs"), methods=["GET", "POST"])
    def testruns_api():
        if request.method == "GET":
            lid = request.args.get('id')
            ltestname = request.args.get('name')
            lstatuses = request.args.get('statuses')
            lcursorWS = request.args.get("cursor")
    
            retval = None
            if lid:
                retval = get_json_testrun_by_id(lid)
                if not retval:
                    return "can't find test run for id %s" % lid, 404
            else:
                retval = get_testruns(ltestname, lstatuses, lcursorWS)
                
            return jsonify(retval)    
        else: # POST
            lbodyJson = request.get_json()
            
            laction = lbodyJson.get("action")
            if laction == "cancel":
                lid = lbodyJson.get("id")
                if not lid:
                    return "id field required", 400
                else:
                    ltestRun = get_testrun_by_id(lid)
                    
                    if not ltestRun:
                        return "can't find test run for id %s" % lid, 404
                    else:
                        cancel_test_run(ltestRun)
                        return "ok", 200
            elif laction == "delete":
                lid = lbodyJson.get("id")
                if not lid:
                    return "id field required", 400
                else:
                    ltestRun = get_testrun_by_id(lid)
                    
                    if not ltestRun:
                        return "can't find test run for id %s" % lid, 404
                    else:
                        logging.debug("here")
                        delete_test_run(ltestRun)
                        return "ok", 200
            else:
                return "unknown action %s" % laction, 400
