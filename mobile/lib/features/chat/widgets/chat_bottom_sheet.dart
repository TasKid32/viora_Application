import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../data/chat_models.dart';
import '../provider/chat_provider.dart';

/// Opens the AI assistant as a professional modal bottom sheet.
///
/// Each open = clean session (messages cleared on close).
/// The backend still provides context from the latest CV analysis.
void showChatBottomSheet(BuildContext context) {
  // Reset local messages for a fresh session
  context.read<ChatProvider>().clearMessages();

  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => ChangeNotifierProvider.value(
      value: context.read<ChatProvider>(),
      child: const _ChatSheet(),
    ),
  ).whenComplete(() {
    // Clean up when sheet is dismissed
    context.read<ChatProvider>().clearMessages();
  });
}

class _ChatSheet extends StatefulWidget {
  const _ChatSheet();
  @override
  State<_ChatSheet> createState() => _ChatSheetState();
}

class _ChatSheetState extends State<_ChatSheet> {
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
    Future.delayed(const Duration(milliseconds: 100), _scrollToBottom);
  }

  void _scrollToBottom() {
    if (_scrollCtrl.hasClients) {
      _scrollCtrl.animateTo(
        _scrollCtrl.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // ── Drag handle ──
          Container(
            margin: const EdgeInsets.only(top: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: AppColors.border,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // ── Header — hero gradient accent ──
          Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(
              gradient: AppColors.heroGradient,
              borderRadius: BorderRadius.circular(AppRadius.lg),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withValues(alpha: 0.2),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.auto_awesome,
                      color: Colors.white, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        AppLocalizations.of(context)!.aiAssistant,
                        style: AppTextStyles.bodyBold
                            .copyWith(color: Colors.white),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        AppLocalizations.of(context)!.askAboutCareer,
                        style: AppTextStyles.caption
                            .copyWith(color: Colors.white70),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    shape: BoxShape.circle,
                  ),
                  child: IconButton(
                    icon:
                        const Icon(Icons.close, color: Colors.white, size: 16),
                    padding: EdgeInsets.zero,
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
              ],
            ),
          ),

          // ── Messages ──
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (_, chat, __) {
                if (chat.messages.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppColors.primaryContainer,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.auto_awesome,
                              size: 40,
                              color: AppColors.primary.withValues(alpha: 0.7)),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          AppLocalizations.of(context)!.askAboutCareer,
                          style: AppTextStyles.body
                              .copyWith(color: AppColors.textHint),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  );
                }
                return ListView.builder(
                  controller: _scrollCtrl,
                  padding: const EdgeInsets.all(16),
                  itemCount: chat.messages.length,
                  itemBuilder: (_, i) => _MessageBubble(msg: chat.messages[i]),
                );
              },
            ),
          ),

          // ── Input area ──
          Container(
            padding: EdgeInsets.only(
                left: 16, right: 16, top: 8, bottom: 8 + bottomInset),
            decoration: BoxDecoration(
              color: AppColors.white,
              border: Border(
                  top: BorderSide(color: AppColors.outlineVariant, width: 1)),
            ),
            child: SafeArea(
              top: false,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Suggestion chips
                  Consumer<ChatProvider>(
                    builder: (_, chat, __) {
                      if (chat.suggestions.isEmpty) {
                        return const SizedBox.shrink();
                      }
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: chat.suggestions
                                .map((s) => Padding(
                                      padding: const EdgeInsetsDirectional.only(
                                          end: 8),
                                      child: ActionChip(
                                        label: Text(s,
                                            style: AppTextStyles.caption
                                                .copyWith(
                                                    color: AppColors.primary)),
                                        backgroundColor:
                                            AppColors.primarySurface,
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
                              borderRadius:
                                  BorderRadius.circular(AppRadius.full),
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
                                  color:
                                      AppColors.primary.withValues(alpha: 0.3),
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
          ),
        ],
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final ChatMsg msg;
  const _MessageBubble({required this.msg});

  @override
  Widget build(BuildContext context) {
    // Error messages from bot get special styling
    final isError = !msg.isUser && msg.isError;

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
          color: isError
              ? AppColors.error.withValues(alpha: 0.08)
              : msg.isUser
                  ? AppColors.primary
                  : AppColors.surfaceTinted,
          borderRadius: BorderRadiusDirectional.only(
            topStart: const Radius.circular(18),
            topEnd: const Radius.circular(18),
            bottomStart: Radius.circular(msg.isUser ? 18 : 4),
            bottomEnd: Radius.circular(msg.isUser ? 4 : 18),
          ),
          border: isError
              ? Border.all(color: AppColors.error.withValues(alpha: 0.3))
              : msg.isUser
                  ? null
                  : Border.all(color: AppColors.outlineVariant),
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
        child: isError
            ? Row(
                children: [
                  Icon(Icons.warning_amber_rounded,
                      size: 18, color: AppColors.error),
                  const SizedBox(width: 8),
                  Expanded(
                    child: SelectableText(
                      msg.text,
                      style: AppTextStyles.body
                          .copyWith(color: AppColors.error, height: 1.5),
                    ),
                  ),
                ],
              )
            : SelectableText(
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
