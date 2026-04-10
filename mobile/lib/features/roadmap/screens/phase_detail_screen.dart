import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../shared/widgets/viora_card.dart';
import '../provider/roadmap_provider.dart';
import '../data/roadmap_api.dart';

/// Detailed view for a single phase — topics + resources.
class PhaseDetailScreen extends StatelessWidget {
  final RoadmapPhase phase;
  const PhaseDetailScreen({super.key, required this.phase});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(phase.phase),
      ),
      body: Consumer<RoadmapProvider>(
        builder: (_, provider, __) {
          // Find the live phase from provider (for state updates)
          final livePhase = provider.data?.phases.firstWhere(
                (p) => p.phase == phase.phase,
                orElse: () => phase,
              ) ??
              phase;

          // Find phase index for toggleResource
          final phaseIndex =
              provider.data?.phases.indexWhere((p) => p.phase == phase.phase) ??
                  -1;

          return SingleChildScrollView(
            padding: AppSpacing.screenPadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Progress header
                _ProgressHeader(phase: livePhase),
                const SizedBox(height: AppSpacing.sectionGap),

                // Topics list
                ...List.generate(livePhase.topics.length, (i) {
                  final topic = livePhase.topics[i];
                  return _TopicSection(
                    topic: topic,
                    phaseIndex: phaseIndex,
                    topicIndex: i,
                  );
                }),

                const SizedBox(height: AppSpacing.fabClearance),
              ],
            ),
          );
        },
      ),
    );
  }
}

// ─── Sub-widgets ────────────────────────────────────────

class _ProgressHeader extends StatelessWidget {
  final RoadmapPhase phase;
  const _ProgressHeader({required this.phase});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final completedTopics = phase.topics.where((t) => t.completed).length;
    final totalTopics = phase.topics.length;
    final totalResources = phase.allResources.length;
    final completedResources =
        phase.allResources.where((r) => r.completed).length;
    final progress =
        totalResources > 0 ? completedResources / totalResources : 0.0;

    return Container(
      width: double.infinity,
      padding: AppSpacing.cardPadding,
      decoration: BoxDecoration(
        gradient: AppColors.heroGradient,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        boxShadow: const [
          BoxShadow(
              color: Color(0x307C3AED), blurRadius: 16, offset: Offset(0, 4)),
        ],
      ),
      child: Row(
        children: [
          // Ring
          SizedBox(
            width: 48,
            height: 48,
            child: Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: progress,
                  strokeWidth: 4,
                  backgroundColor: Colors.white.withValues(alpha: 0.25),
                  valueColor: const AlwaysStoppedAnimation(Colors.white),
                  strokeCap: StrokeCap.round,
                ),
                Text(
                  '${(progress * 100).toInt()}%',
                  style: AppTextStyles.caption.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(l10n.overallProgress,
                    style:
                        AppTextStyles.bodyBold.copyWith(color: Colors.white)),
                const SizedBox(height: 4),
                Text(
                  '$completedTopics/$totalTopics ${l10n.topics}  •  $completedResources/$totalResources ${l10n.resourcesCompleted}',
                  style: AppTextStyles.caption.copyWith(color: Colors.white70),
                ),
              ],
            ),
          ),
          if (phase.duration.isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(AppRadius.full),
              ),
              child: Text(phase.duration,
                  style: AppTextStyles.caption.copyWith(color: Colors.white)),
            ),
        ],
      ),
    );
  }
}

class _TopicSection extends StatelessWidget {
  final TopicResources topic;
  final int phaseIndex;
  final int topicIndex;

  const _TopicSection({
    required this.topic,
    required this.phaseIndex,
    required this.topicIndex,
  });

  @override
  Widget build(BuildContext context) {
    final isCompleted = topic.completed;

    return VioraCard(
      padding: EdgeInsets.zero,
      margin: const EdgeInsets.only(bottom: 12),
      borderColor:
          isCompleted ? AppColors.success.withValues(alpha: 0.3) : null,
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          initiallyExpanded: !isCompleted && topicIndex == 0,
          tilePadding: const EdgeInsets.symmetric(horizontal: 16),
          childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          leading: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: isCompleted
                  ? AppColors.success.withValues(alpha: 0.1)
                  : AppColors.primarySurface,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: isCompleted
                  ? const Icon(Icons.check, color: AppColors.success, size: 16)
                  : Text('${topicIndex + 1}',
                      style: AppTextStyles.bodySmallBold
                          .copyWith(color: AppColors.primary)),
            ),
          ),
          title: Text(
            topic.name,
            style: AppTextStyles.bodyBold.copyWith(
              color: isCompleted ? AppColors.success : AppColors.textPrimary,
            ),
          ),
          children: List.generate(topic.resources.length, (rIndex) {
            return _ResourceCard(
              resource: topic.resources[rIndex],
              phaseIndex: phaseIndex,
              topicIndex: topicIndex,
              resourceIndex: rIndex,
            );
          }),
        ),
      ),
    );
  }
}

class _ResourceCard extends StatelessWidget {
  final LearningResource resource;
  final int phaseIndex;
  final int topicIndex;
  final int resourceIndex;

  const _ResourceCard({
    required this.resource,
    required this.phaseIndex,
    required this.topicIndex,
    required this.resourceIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: resource.completed
            ? AppColors.success.withValues(alpha: 0.04)
            : AppColors.surfaceVariant.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(
          color: resource.completed
              ? AppColors.success.withValues(alpha: 0.2)
              : AppColors.outlineVariant,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          // Completion checkbox
          GestureDetector(
            onTap: () {
              if (phaseIndex >= 0) {
                context.read<RoadmapProvider>().toggleResource(
                      phaseIndex,
                      topicIndex,
                      resourceIndex,
                    );
              }
            },
            child: Container(
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                color:
                    resource.completed ? AppColors.success : Colors.transparent,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: resource.completed
                      ? AppColors.success
                      : AppColors.outline,
                  width: 1.5,
                ),
              ),
              child: resource.completed
                  ? const Icon(Icons.check, color: Colors.white, size: 14)
                  : null,
            ),
          ),
          const SizedBox(width: 12),
          // Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  resource.title,
                  style: AppTextStyles.body.copyWith(
                    color: resource.completed
                        ? AppColors.textHint
                        : AppColors.textPrimary,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),
                // Metadata row — simpler with just text badges
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: [
                    if (resource.platform.isNotEmpty)
                      _tag(resource.platform, AppColors.info),
                    if (resource.type.isNotEmpty)
                      _tag(resource.type, AppColors.primary),
                    if (resource.duration != null &&
                        resource.duration!.isNotEmpty)
                      _tag(resource.duration!, AppColors.textSecondary),
                  ],
                ),
              ],
            ),
          ),
          // Open link
          if (resource.url.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.open_in_new,
                  size: 18, color: AppColors.primary),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
              onPressed: () => launchUrl(Uri.parse(resource.url),
                  mode: LaunchMode.externalApplication),
            ),
        ],
      ),
    );
  }

  Widget _tag(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(AppRadius.sm),
      ),
      child: Text(
        text,
        style: AppTextStyles.caption.copyWith(color: color, fontSize: 11),
      ),
    );
  }
}
