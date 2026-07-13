"""TouchDesigner DAT script adapter for the ATLAS visual event hub.

Attach these callbacks to a Web Client DAT pointed at:
ws://127.0.0.1:8000/api/atlas/visual/ws
"""
import json


def _set(name, value):
    op(name).par.value0 = value if op(name) is not None else value


def onConnect(dat):
    parent().store('atlas_connected', True)
    return


def onDisconnect(dat):
    parent().store('atlas_connected', False)
    return


def onReceiveText(dat, rowIndex, message):
    try:
        envelope = json.loads(message)
    except Exception:
        return

    payload = envelope.get('payload', {})
    parent().store('atlas_last_event', envelope.get('event', 'unknown'))
    parent().store('atlas_persona', payload.get('persona', 'atlas'))
    parent().store('atlas_state', payload.get('state', 'idle'))
    parent().store('atlas_intensity', float(payload.get('intensity', 0.0)))
    parent().store('atlas_progress', float(payload.get('progress', 0.0)))
    parent().store('atlas_mode', payload.get('mode', 'core'))
    return


def onReceiveBinary(dat, contents):
    return


def onError(dat, error):
    parent().store('atlas_error', str(error))
    return
