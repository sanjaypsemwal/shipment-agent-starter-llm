import requests
TESTS=[("Where is my package and when will it arrive?","policies"),("Status for ORD-1001 please","orders")]
if __name__=="__main__":
    passed=0
    for i,(goal,kind) in enumerate(TESTS,1):
        r=requests.post("http://localhost:8000/agent/run", json={"goal":goal,"max_steps":3})
        js=r.json(); ok=r.status_code==200 and "steps" in js and (js.get("answer") or js.get("follow_up"))
        passed+=1 if ok else 0
        print(f"[{i}] {kind}: status={r.status_code}, steps={js.get('steps')}, answer={js.get('answer')}")
    print(f"Passed {passed}/{len(TESTS)}")
