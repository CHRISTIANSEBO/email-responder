import json
import sqlite3
import threading
import uuid
from pathlib import Path
from flask import Flask, request, jsonify
from langgraph.checkpoint.memory import MemorySaver
from agent.assistant import create_agent
import builtins as _builtins

app = Flask(__name__)
checkpointer = MemorySaver()
agent = create_agent(checkpointer=checkpointer)

_DB_PATH = Path(__file__).parent / 'chats.db'


def _db():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                messages TEXT NOT NULL DEFAULT '[]',
                thread_id TEXT NOT NULL,
                created_at REAL NOT NULL DEFAULT (unixepoch('now'))
            )
        """)


_init_db()

_lock = threading.Lock()
_thread_id = "web"
_state = {
    'active_rid': None,
    'pending_prompt': None,
    'input_event': None,
    'input_response': None,
    'ready': threading.Event(),
    'result': None,
    'error': None,
}


def _make_web_input(rid: str):
    def _web_input(prompt: str) -> str:
        with _lock:
            if _state['active_rid'] != rid:
                return 'n'
        input_event = threading.Event()
        with _lock:
            _state['pending_prompt'] = prompt
            _state['input_event'] = input_event
            _state['input_response'] = None
        _state['ready'].set()
        input_event.wait()
        return _state['input_response'] or 'n'
    return _web_input


def _run_agent(user_input: str, rid: str) -> None:
    global _thread_id
    original_input = _builtins.input
    _builtins.input = _make_web_input(rid)
    try:
        with _lock:
            tid = _thread_id
        try:
            response = agent.invoke(
                {'messages': [{'role': 'user', 'content': user_input}]},
                config={"configurable": {"thread_id": tid}}
            )
        except ValueError as e:
            if 'INVALID_CHAT_HISTORY' not in str(e):
                raise
            with _lock:
                _thread_id = f"web-{uuid.uuid4().hex[:8]}"
                tid = _thread_id
            response = agent.invoke(
                {'messages': [{'role': 'user', 'content': user_input}]},
                config={"configurable": {"thread_id": tid}}
            )
        with _lock:
            if _state['active_rid'] == rid:
                _state['result'] = response['messages'][-1].content
                _state['error'] = None
    except Exception as e:
        msg = str(e)
        if '429' in msg or 'rate_limit' in msg.lower():
            err = "I'm being rate-limited right now. Wait a moment and try again."
        else:
            err = f"Something went wrong: {type(e).__name__}: {e}"
        with _lock:
            if _state['active_rid'] == rid:
                _state['error'] = err
                _state['result'] = None
    finally:
        _builtins.input = original_input
        with _lock:
            if _state['active_rid'] == rid:
                _state['ready'].set()


def _wait_for_agent() -> dict:
    timeout = 120  # seconds
    deadline = threading.Event()

    def _expire():
        deadline.set()

    timer = threading.Timer(timeout, _expire)
    timer.start()
    try:
        while not deadline.is_set():
            _state['ready'].wait(timeout=1)
            _state['ready'].clear()
            with _lock:
                if _state['input_event'] and not _state['input_event'].is_set():
                    return {'type': 'confirmation', 'prompt': _state['pending_prompt'], 'reply': ''}
                if _state['error'] is not None:
                    return {'type': 'message', 'reply': _state['error']}
                if _state['result'] is not None:
                    return {'type': 'message', 'reply': _state['result']}
    finally:
        timer.cancel()
    return {'type': 'message', 'reply': 'Request timed out. Please try again.'}


@app.route('/chats', methods=['GET'])
def list_chats():
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, title FROM chats ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/chats/<chat_id>', methods=['GET'])
def get_chat(chat_id: str):
    with _db() as conn:
        row = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    data = dict(row)
    data['messages'] = json.loads(data['messages'])
    return jsonify(data)


@app.route('/chats/<chat_id>/save', methods=['POST'])
def save_chat(chat_id: str):
    body = request.json or {}
    messages = body.get('messages', [])
    title = body.get('title', 'Untitled')
    with _db() as conn:
        conn.execute("""
            INSERT INTO chats (id, title, messages, thread_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET messages = excluded.messages, title = excluded.title
        """, (chat_id, title, json.dumps(messages), body.get('thread_id', '')))
    return jsonify({'ok': True})


@app.route('/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id: str):
    with _db() as conn:
        conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    return jsonify({'ok': True})


@app.route('/chat', methods=['POST'])
def chat():
    global _thread_id
    body = request.json or {}
    user_input = body.get('message', '').strip()
    chat_id = body.get('chat_id') or None
    if not user_input:
        return jsonify({'error': 'Empty message'}), 400

    # Restore thread_id for existing chats
    if chat_id:
        with _db() as conn:
            row = conn.execute("SELECT thread_id FROM chats WHERE id = ?", (chat_id,)).fetchone()
        if row and row['thread_id']:
            with _lock:
                _thread_id = row['thread_id']
    else:
        chat_id = uuid.uuid4().hex
        with _lock:
            tid = _thread_id
        with _db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO chats (id, title, messages, thread_id) VALUES (?, ?, ?, ?)",
                (chat_id, user_input[:60], '[]', tid)
            )

    rid = uuid.uuid4().hex
    with _lock:
        old_event = _state['input_event']
        if old_event and not old_event.is_set():
            _state['input_response'] = 'n'
            _state['input_event'] = None
            _thread_id = f"web-{uuid.uuid4().hex[:8]}"
            old_event.set()
        _state['active_rid'] = rid
        _state['result'] = None
        _state['error'] = None
        _state['pending_prompt'] = None
        _state['input_event'] = None
    _state['ready'].clear()
    threading.Thread(target=_run_agent, args=(user_input, rid), daemon=True).start()
    result = _wait_for_agent()
    result['chat_id'] = chat_id
    with _lock:
        result['thread_id'] = _thread_id
    return jsonify(result)


@app.route('/confirm', methods=['POST'])
def confirm():
    answer = 'y' if request.json.get('confirmed') else 'n'
    with _lock:
        event = _state['input_event']
        if not event or event.is_set():
            return jsonify({'error': 'No pending confirmation'}), 400
        _state['input_response'] = answer
        _state['input_event'] = None
    _state['ready'].clear()
    event.set()
    return jsonify(_wait_for_agent())


if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, threaded=True, port=5000)
