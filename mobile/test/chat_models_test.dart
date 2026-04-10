import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/features/chat/data/chat_models.dart';

void main() {
  group('ChatMsg', () {
    test('creates user message with current time', () {
      final msg = ChatMsg(text: 'Hello', isUser: true);

      expect(msg.text, 'Hello');
      expect(msg.isUser, true);
      expect(msg.time, isNotNull);
      expect(msg.time.difference(DateTime.now()).inSeconds.abs(), lessThan(2));
    });

    test('creates bot message with custom time', () {
      final customTime = DateTime(2026, 3, 18, 12, 0);
      final msg = ChatMsg(text: 'Hi there', isUser: false, time: customTime);

      expect(msg.text, 'Hi there');
      expect(msg.isUser, false);
      expect(msg.time, customTime);
    });
  });
}
