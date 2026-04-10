import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../shared/widgets/viora_card.dart';
import '../../../shared/widgets/viora_empty_state.dart';
import '../../../shared/widgets/viora_section_header.dart';
import '../provider/roadmap_provider.dart';
import '../data/roadmap_api.dart';
import 'phase_detail_screen.dart';

/// Roadmap screen — shows learning phases as a timeline.
class RoadmapScreen extends StatefulWidget {
  const RoadmapScreen({super.key});

  @override
  State<RoadmapScreen> createState() => _RoadmapScreenState();
}

class _RoadmapScreenState extends State<RoadmapScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<RoadmapProvider>().load());
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.navRoadmap),
      ),
      body: Consumer<RoadmapProvider>(
        builder: (_, provider, __) {
          if (provider.loading) {
            return const Center(
                child: CircularProgressIndicator(color: AppColors.primary));
          }

          if (provider.error != null && provider.data == null) {
            return VioraEmptyState(
              icon: Icons.error_outline,
              title: provider.error ?? l10n.retry,
              actionLabel: l10n.retry,
              onAction: () => provider.load(),
            );
          }

          if (provider.data == null || provider.data!.phases.isEmpty) {
            return VioraEmptyState(
              icon: Icons.map_outlined,
              title: l10n.noRoadmapAvailable,
              subtitle: l10n.analyzeFirst,
            );
          }

          final data = provider.data!;

          return RefreshIndicator(
            onRefresh: () => provider.load(),
            color: AppColors.primary,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: AppSpacing.screenPadding,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Overall progress card
                  _OverallProgress(data: data),
                  const SizedBox(height: AppSpacing.sectionGap),

                  // Timeline section header
                  VioraSectionHeader(
                      title: l10n.learningPhases,
                      icon: Icons.route,
                      color: AppColors.primary),
                  const SizedBox(height: AppSpacing.lg),

                  // Phase cards as timeline
                  ...List.generate(data.phases.length, (i) {
                    final phase = data.phases[i];
                    final isLast = i == data.phases.length - 1;
                    return _PhaseTimelineItem(
                      phase: phase,
                      index: i,
                      isLast: isLast,
                      onTap: () => _openPhaseDetail(phase),
                    );
                  }),

                  // FAB clearance
                  const SizedBox(height: 72),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  void _openPhaseDetail(RoadmapPhase phase) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ChangeNotifierProvider.value(
          value: context.read<RoadmapProvider>(),
          child: PhaseDetailScreen(phase: phase),
        ),
      ),
    );
  }
}

// ─── Sub-widgets ────────────────────────────────────────

class _OverallProgress extends StatelessWidget {
  final RoadmapData data;
  const _OverallProgress({required this.data});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final totalTopics =
        data.phases.fold<int>(0, (sum, p) => sum + p.topics.length);
    final completedTopics = data.phases.fold<int>(
        0, (sum, p) => sum + p.topics.where((t) => t.completed).length);
    final totalResources =
        data.phases.fold<int>(0, (sum, p) => sum + p.allResources.length);
    final completedResources = data.phases.fold<int>(
        0, (sum, p) => sum + p.allResources.where((r) => r.completed).length);
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              SizedBox(
                width: 52,
                height: 52,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    SizedBox(
                      width: 52,
                      height: 52,
                      child: CircularProgressIndicator(
                        value: progress,
                        strokeWidth: 4,
                        backgroundColor: Colors.white.withValues(alpha: 0.25),
                        valueColor: const AlwaysStoppedAnimation(Colors.white),
                        strokeCap: StrokeCap.round,
                      ),
                    ),
                    Text(
                      '${(progress * 100).toInt()}%',
                      style: AppTextStyles.bodySmallBold
                          .copyWith(color: Colors.white),
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
                        style: AppTextStyles.bodyBold
                            .copyWith(color: Colors.white)),
                    const SizedBox(height: 4),
                    Text(
                      '$completedTopics ${l10n.of_} $totalTopics ${l10n.topics}  •  $completedResources ${l10n.of_} $totalResources ${l10n.resourcesCompleted}',
                      style:
                          AppTextStyles.caption.copyWith(color: Colors.white70),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          ClipRRect(
            borderRadius: BorderRadius.circular(AppRadius.sm),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 5,
              backgroundColor: Colors.white.withValues(alpha: 0.25),
              valueColor: const AlwaysStoppedAnimation(Colors.white),
            ),
          ),
        ],
      ),
    );
  }
}

/// Single phase item in the timeline.
class _PhaseTimelineItem extends StatelessWidget {
  final RoadmapPhase phase;
  final int index;
  final bool isLast;
  final VoidCallback onTap;

  const _PhaseTimelineItem({
    required this.phase,
    required this.index,
    required this.isLast,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final completedTopics = phase.topics.where((t) => t.completed).length;
    final totalTopics = phase.topics.length;
    final progress = totalTopics > 0 ? completedTopics / totalTopics : 0.0;
    final isDone = completedTopics == totalTopics && totalTopics > 0;
    final pColor = _priorityColor(phase.priority);

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline indicator column
          SizedBox(
            width: 44,
            child: Column(
              children: [
                // Phase number circle
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    color: isDone
                        ? AppColors.success
                        : progress > 0
                            ? AppColors.primary
                            : AppColors.surfaceVariant,
                    shape: BoxShape.circle,
                    boxShadow: progress > 0
                        ? [
                            BoxShadow(
                              color: (isDone
                                      ? AppColors.success
                                      : AppColors.primary)
                                  .withValues(alpha: 0.25),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ]
                        : null,
                  ),
                  child: Center(
                    child: isDone
                        ? const Icon(Icons.check, color: Colors.white, size: 20)
                        : Text(
                            '${index + 1}',
                            style: AppTextStyles.bodyBold.copyWith(
                              color: progress > 0
                                  ? Colors.white
                                  : AppColors.textHint,
                              fontSize: 15,
                            ),
                          ),
                  ),
                ),
                // Connector line
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 3,
                      margin: const EdgeInsets.symmetric(vertical: 4),
                      decoration: BoxDecoration(
                        color: isDone
                            ? AppColors.success.withValues(alpha: 0.3)
                            : AppColors.outlineVariant,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          // Card content
          Expanded(
            child: Container(
              margin: EdgeInsets.only(bottom: isLast ? 0 : 14),
              child: VioraCard(
                onTap: onTap,
                color: progress > 0 && !isDone ? AppColors.surfaceTinted : null,
                padding: const EdgeInsets.all(16),
                borderColor: isDone
                    ? AppColors.success.withValues(alpha: 0.3)
                    : progress > 0
                        ? AppColors.primary.withValues(alpha: 0.15)
                        : null,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title
                    Text(phase.phase, style: AppTextStyles.h4),
                    const SizedBox(height: 10),

                    // Stats row — duration, topics, priority
                    Wrap(
                      spacing: 8,
                      runSpacing: 6,
                      children: [
                        if (phase.duration.isNotEmpty)
                          _phaseChip(Icons.schedule, phase.duration,
                              AppColors.primary),
                        _phaseChip(
                          Icons.library_books_outlined,
                          '$totalTopics ${l10n.topics}',
                          AppColors.textSecondary,
                        ),
                        if (phase.priority.isNotEmpty)
                          _phaseChip(
                            Icons.flag_outlined,
                            phase.priority,
                            pColor,
                            isBold: true,
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Progress strip
                    Row(
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(3),
                            child: LinearProgressIndicator(
                              value: progress,
                              minHeight: 4,
                              backgroundColor: AppColors.outlineVariant,
                              valueColor: AlwaysStoppedAnimation(
                                isDone ? AppColors.success : AppColors.primary,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          '$completedTopics/$totalTopics',
                          style: AppTextStyles.bodySmallBold.copyWith(
                            color: isDone
                                ? AppColors.success
                                : AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(width: 2),
                        Icon(
                            Directionality.of(context) == TextDirection.rtl
                                ? Icons.chevron_left
                                : Icons.chevron_right,
                            size: 18,
                            color: AppColors.textHint),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _phaseChip(IconData icon, String text, Color color,
      {bool isBold = false}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(AppRadius.full),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: color),
          const SizedBox(width: 4),
          Text(text,
              style: AppTextStyles.caption.copyWith(
                color: color,
                fontWeight: isBold ? FontWeight.w700 : FontWeight.w500,
                fontSize: 11,
              )),
        ],
      ),
    );
  }

  Color _priorityColor(String priority) {
    switch (priority.toLowerCase()) {
      case 'high':
        return AppColors.error;
      case 'medium':
        return AppColors.warning;
      default:
        return AppColors.info;
    }
  }
}
