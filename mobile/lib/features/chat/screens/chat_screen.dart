import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../data/chat_models.dart';
import '../provider/chat_provider.dart';

/// Chat screen — full-page AI assistant conversation.
class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _ctrl = TextEditingController();
  final _scrollCtrl = ScrollController();

  @override
  void dispose() {
    _ctrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  void _send() {
    final text = _ctrl.text.trim();
    if (text.isEmpty) return;
    context.read<ChatProvider>().send(text);
    _ctrl.clear();
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.aiAssistant),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_comment_outlined,
                color: AppColors.primary),
            tooltip: AppLocalizations.of(context)!.newChat,
            onPressed: () => context.read<ChatProvider>().clearMessages(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Messages
          Expanded(
            child: Selector<ChatProvider, int>(
              selector: (_, p) => p.messages.length,
              builder: (_, msgCount, __) {
                final chat = context.read<ChatProvider>();
                if (chat.messages.isEmpty) {
                  return _buildEmptyState();
                }
                return ListView.builder(
                  controller: _scrollCtrl,
                  padding: const EdgeInsets.all(16),
                  itemCount: msgCount,
                  itemBuilder: (_, i) => _MessageBubble(msg: chat.messages[i]),
                );
              },
            ),
          ),

          // Input area
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Brand-tinted icon circle
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: AppColors.primaryContainer,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.auto_awesome,
                size: 32, color: AppColors.primary),
          ),
          const SizedBox(height: 16),
          Text(
            AppLocalizations.of(context)!.askAboutCareer,
            style: AppTextStyles.body.copyWith(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.white,
        border:
            Border(top: BorderSide(color: AppColors.outlineVariant, width: 1)),
      ),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Suggestion chips
            Consumer<ChatProvider>(
              builder: (_, chat, __) {
                if (chat.suggestions.isEmpty) return const SizedBox.shrink();
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: chat.suggestions
                          .map((s) => Padding(
                                padding:
                                    const EdgeInsetsDirectional.only(end: 8),
                                child: ActionChip(
                                  label: Text(s,
                                      style: AppTextStyles.caption
                                          .copyWith(color: AppColors.primary)),
                                  backgroundColor: AppColors.primarySurface,
                                  side: BorderSide.none,
                                  onPressed: () {
                                    _ctrl.text = s;
                                    _send();
                                  },
                                ),
                              ))
                          .toList(),
                    ),
                  ),
                );
              },
            ),
            // Text input + send button
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ctrl,
                    style: AppTextStyles.body,
                    decoration: InputDecoration(
                      hintText: AppLocalizations.of(context)!.typeMessage,
                      hintStyle: AppTextStyles.body
                          .copyWith(color: AppColors.textHint),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppRadius.full),
                        borderSide: BorderSide.none,
                      ),
                      fillColor: AppColors.surfaceTinted,
                      filled: true,
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 10),
                    ),
                    onSubmitted: (_) => _send(),
                    textInputAction: TextInputAction.send,
                  ),
                ),
                const SizedBox(width: 8),
                Selector<ChatProvider, bool>(
                  selector: (_, p) => p.sending,
                  builder: (_, sending, __) {
                    return Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        gradient: AppColors.heroGradient,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.primary.withValues(alpha: 0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: IconButton(
                        onPressed: sending ? null : _send,
                        icon: sending
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                    color: Colors.white, strokeWidth: 2),
                              )
                            : const Icon(Icons.send,
                                color: Colors.white, size: 20),
                        padding: EdgeInsets.zero,
                      ),
                    );
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final ChatMsg msg;
  const _MessageBubble({required this.msg});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: msg.isUser
          ? AlignmentDirectional.centerEnd
          : AlignmentDirectional.centerStart,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints:
            BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
        decoration: BoxDecoration(
          color: msg.isUser ? AppColors.primary : AppColors.surfaceTinted,
          borderRadius: BorderRadiusDirectional.only(
            topStart: const Radius.circular(18),
            topEnd: const Radius.circular(18),
            bottomStart: Radius.circular(msg.isUser ? 18 : 4),
            bottomEnd: Radius.circular(msg.isUser ? 4 : 18),
          ),
          border:
              msg.isUser ? null : Border.all(color: AppColors.outlineVariant),
          boxShadow: [
            BoxShadow(
              color: msg.isUser
                  ? AppColors.primary.withValues(alpha: 0.2)
                  : Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Text(
          msg.text,
          style: AppTextStyles.body.copyWith(
            color: msg.isUser ? Colors.white : AppColors.textPrimary,
            height: 1.5,
          ),
        ),
      ),
    );
  }
}
