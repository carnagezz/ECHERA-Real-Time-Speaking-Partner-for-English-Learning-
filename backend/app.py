from __future__ import annotations
import os
from flask import Flask, request, jsonify, send_from_directory

from database import Database
from auth_service import AuthService
from account_controller import AccountController
from ai_service import AIService
from nlp_engine import NLPEngine
from message_controller import MessageController
from conversation_controller import ConversationController
from settings_controller import SettingsController
from profile_controller import ProfileController

def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="")

    connectionString = os.getenv(
        "DATABASE_URL",
        "dbname=seng321 user=postgres password=011186 host=localhost port=5432"
    )
    db = Database(connectionString)

    authService = AuthService(db)
    accountController = AccountController(db, authService)

    aiService = AIService(os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat"))
    mlEngine = NLPEngine("")

    messageController = MessageController(db, aiService, mlEngine)
    conversationController = ConversationController(db, aiService, messageController)
    settingsController = SettingsController(db)
    profileController = ProfileController(db)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.post("/api/account/register")
    def register():
        data = request.get_json(force=True) or {}
        try:
            result = accountController.register(
                data.get("email", ""),
                data.get("password", ""),
                data.get("nickname", "")
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/account/login")
    def login():
        data = request.get_json(force=True) or {}
        try:
            result = accountController.login(
                data.get("email", ""),
                data.get("password", "")
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/account/logout")
    def logout():
        data = request.get_json(force=True) or {}
        try:
            result = accountController.logout(data.get("sessionId", ""))
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/account/updateProfile")
    def update_profile():
        data = request.get_json(force=True) or {}
        try:
            result = accountController.updateProfile(
                data.get("userId", ""),
                data.get("data") or {}
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/conversations")
    def create_conversation():
        data = request.get_json(force=True) or {}
        try:
            result = conversationController.createConversation(data.get("userId", ""))
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.get("/api/conversations")
    def get_history():
        userId = request.args.get("userId", "")
        try:
            conversations = conversationController.getHistory(userId)
            return jsonify({"conversations": conversations})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.get("/api/conversations/<conversationId>")
    def get_details(conversationId: str):
        try:
            result = conversationController.getDetails(conversationId)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.delete("/api/conversations/<conversationId>")
    def delete_conversation(conversationId: str):
        try:
            result = conversationController.delete(conversationId)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/conversations/<conversationId>/first-title")
    def first_title(conversationId: str):
        data = request.get_json(force=True) or {}
        try:
            title = conversationController.processFirstMessage(data.get("text", ""))
            db.updateTitle(conversationId, title)
            return jsonify({"title": title})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/messages/send")
    def send_message():
        data = request.get_json(force=True) or {}
        try:
            messageController._setActive(
                data.get("conversationId", ""),
                data.get("userId", "")
            )
            
            result = messageController.sendMessage(data.get("text", ""))
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.get("/api/profile/statistics")
    def profile_stats():
        userId = request.args.get("userId", "")
        try:
            result = profileController.getStatistics(userId)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.get("/api/settings/load")
    def load_settings():
        userId = request.args.get("userId", "")
        try:
            result = settingsController.loadVoiceSettings(userId)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/settings/preview")
    def preview_voice():
        """Preview voice (handled in frontend via Web Speech API)"""
        # This endpoint exists for API consistency but actual preview happens in browser
        return jsonify({"ok": True})

    @app.post("/api/settings/save")
    def save_voice():
        data = request.get_json(force=True) or {}
        try:
            result = settingsController.saveVoicePreference(
                data.get("userId", ""),
                data.get("voiceId", "")
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)