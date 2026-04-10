/// Chat message model.
class ChatMsg {
  final String text;
  final bool isUser;
  final bool isError;
  final DateTime time;
  ChatMsg({required this.text, required this.isUser, this.isError = false, DateTime? time})
    : time = time ?? DateTime.now();
}
