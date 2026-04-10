import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../core/utils/logger.dart';
import '../../../core/utils/error_helper.dart';
import '../data/chat_api.dart';
import '../data/chat_models.dart';

/// Chat provider — manages conversation state.
///
/// Redesigned for bottom sheet UX:
/// - Each open = clean session (no history loading)
/// - clearMessages() on open and close
/// - deleteHistory() calls backend to clear stored history
class ChatProvider extends ChangeNotifier {
  final ChatApi _api;
  ChatProvider({required ChatApi api}) : _api = api;

  final List<ChatMsg> _messages = [];
  bool _sending = false;
  List<String> _suggestions = [];

  List<ChatMsg> get messages => _messages;
  bool get sending => _sending;
  List<String> get suggestions => _suggestions;

  /// Clear all local messages for a fresh session.
  void clearMessages() {
    _messages.clear();
    _suggestions = [];
    notifyListeners();
  }

  /// Send message to AI assistant.
  Future<void> send(String text) async {
    if (text.trim().isEmpty) return;

    _messages.add(ChatMsg(text: text, isUser: true));
    _sending = true;
    _suggestions = []; // Clear previous suggestions
    notifyListeners();

    try {
      final data = await _api.sendMessage(text);
      final reply = data['reply'] as String? ?? 'Unable to respond right now';
      final rawSuggestions = data['suggestions'] as List? ?? [];
      _suggestions = rawSuggestions.map((s) => s.toString()).toList();
      _messages.add(ChatMsg(text: reply, isUser: false));
    } on DioException catch (e) {
      final errorMsg = extractDioError(e);
      _messages.add(ChatMsg(text: errorMsg, isUser: false, isError: true));
      Log.e('Chat', 'Send failed', e.message);
    } catch (e) {
      _messages.add(ChatMsg(text: 'An unexpected error occurred', isUser: false, isError: true));
      Log.e('Chat', 'Send unexpected error', e);
    }

    _sending = false;
    notifyListeners();
  }

  /// Delete all chat history on the backend.
  /// Called when user re-analyzes their CV.
  Future<void> deleteHistory() async {
    try {
      await _api.deleteHistory();
      clearMessages();
      Log.d('Chat', 'History cleared on backend');
    } catch (e) {
      Log.e('Chat', 'Failed to clear history', e);
    }
  }
}
