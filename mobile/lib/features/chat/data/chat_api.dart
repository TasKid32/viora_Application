import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

/// Chat API — thin wrapper around ApiClient.
class ChatApi {
  final ApiClient _api;
  ChatApi(this._api);

  /// Send message and get AI reply.
  Future<Map<String, dynamic>> sendMessage(String message) async {
    final response = await _api.post(Endpoints.chatSend, data: {'message': message});
    return response.data;
  }

  /// Load chat history.
  Future<List<dynamic>> getHistory() async {
    final response = await _api.get(Endpoints.chatHistory);
    return response.data['chats'] as List? ?? [];
  }

  /// Delete all chat history on the backend.
  Future<void> deleteHistory() async {
    await _api.delete(Endpoints.chatClear);
  }
}
