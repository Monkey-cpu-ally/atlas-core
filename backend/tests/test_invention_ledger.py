from services import invention_ledger as ledger

def setup_function(): ledger.reset_in_memory_state()

def test_ledger_records_provenance_without_claiming_truth():
    item=ledger.create_ledger(title="Adaptive structure",investigation_id="DX-1",subjects=["Robotics"])
    assert item["events"]==[]; assert "does not prove novelty" in item["claim_rule"]

def test_events_form_verifiable_hash_chain():
    item=ledger.create_ledger(title="Adaptive structure",investigation_id="DX-1")
    first=ledger.append_event(item["ledger_id"],event_type="QUESTION",payload={"question":"Can A improve B?"},actor="Minerva")
    second=ledger.append_event(item["ledger_id"],event_type="HYPOTHESIS",payload={"statement":"A improves B"},actor="Hermes",source_refs=["SRC-1"])
    assert second["previous_hash"]==first["event_hash"]
    verified=ledger.verify_chain(item["ledger_id"]); assert verified["valid"] is True; assert verified["event_count"]==2

def test_tampering_is_detected():
    item=ledger.create_ledger(title="Adaptive structure",investigation_id="DX-1")
    ledger.append_event(item["ledger_id"],event_type="EXPERIMENT_RESULT",payload={"value":1},actor="Hermes")
    item["events"][0]["payload"]["value"]=999
    assert ledger.verify_chain(item["ledger_id"])["valid"] is False

def test_unknown_event_type_fails():
    item=ledger.create_ledger(title="Adaptive structure",investigation_id="DX-1")
    try: ledger.append_event(item["ledger_id"],event_type="MAGIC_PROOF",payload={},actor="Council")
    except ledger.InventionLedgerError as exc: assert "invalid event_type" in str(exc)
    else: raise AssertionError("unknown ledger event must fail")
