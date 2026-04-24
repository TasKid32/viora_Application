import 'package:flutter/material.dart';
import 'package:viora_app/core/config/environment.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../core/routing/app_router.dart';
import '../../../shared/widgets/viora_card.dart';
import '../../../shared/widgets/viora_section_header.dart';
import '../provider/dashboard_provider.dart';
import '../data/dashboard_api.dart';

/// Dashboard screen — answers "What am I good at?" + "What should I learn?"
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<DashboardProvider>().load());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Selector<DashboardProvider, bool>(
          selector: (_, p) => p.loading,
          builder: (_, loading, __) {
            if (loading) {
              return const Center(
                  child: CircularProgressIndicator(color: AppColors.primary));
            }

            final provider = context.read<DashboardProvider>();
            final data = provider.data;
            if (data == null) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline,
                        size: 48, color: AppColors.error),
                    const SizedBox(height: 16),
                    Text(provider.error ?? 'Error', style: AppTextStyles.body),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => context.read<DashboardProvider>().load(),
                      child: Text(AppLocalizations.of(context)!.retry),
                    ),
                  ],
                ),
              );
            }

            return RefreshIndicator(
              onRefresh: () => context.read<DashboardProvider>().load(),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: AppSpacing.screenPadding,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header with avatar + greeting
                    _buildHeader(data),
                    const SizedBox(height: AppSpacing.sectionGap),

                    // Learning Progress card
                    _buildProgressCard(data),
                    const SizedBox(height: AppSpacing.sectionGap),

                    // Quick actions
                    VioraSectionHeader(
                        title: AppLocalizations.of(context)!.getStarted,
                        icon: Icons.rocket_launch_outlined),
                    const SizedBox(height: AppSpacing.itemGap),
                    _buildQuickActions(context, data),
                    const SizedBox(height: 16),

                    // Journey steps
                    _buildJourneySteps(data),

                    // FAB clearance
                    const SizedBox(height: 72),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildHeader(DashboardData data) {
    final l10n = AppLocalizations.of(context)!;

    return Row(
      children: [
        // Avatar with gradient border + glow
        Container(
          padding: const EdgeInsets.all(3),
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              colors: [
                AppColors.primary,
                AppColors.accent,
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withValues(alpha:0.35),
                blurRadius: 18,
                spreadRadius: 3,
              ),
            ],
          ),
          child: CircleAvatar(
            radius: 24,
            backgroundColor: AppColors.primarySurface,
            backgroundImage: data.avatarUrl != null &&
                    data.avatarUrl!.isNotEmpty
                ? NetworkImage(
                    "${Environment.apiBaseUrl}${data.avatarUrl}") //Add avatar URL prefix
                : null,
            child: data.avatarUrl == null || data.avatarUrl!.isEmpty
                ? Text(
                    data.userName.isNotEmpty
                        ? data.userName[0].toUpperCase()
                        : '?',
                    style: AppTextStyles.h3.copyWith(color: AppColors.primary),
                  )
                : null,
          ),
        ),

        const SizedBox(width: 14),

        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${l10n.welcomeBack} 👋',
                style: AppTextStyles.h3.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                data.userName,
                style: AppTextStyles.h2.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),

        // Notifications badge (بدون تغيير)
        Stack(
          children: [
            IconButton(
              icon: const Icon(Icons.notifications_outlined,
                  color: AppColors.textSecondary),
              onPressed: () => context.push(Routes.notifications),
            ),
            if (data.notificationsCount > 0)
              Positioned(
                right: 8,
                top: 8,
                child: Container(
                  width: 18,
                  height: 18,
                  decoration: const BoxDecoration(
                      color: AppColors.error, shape: BoxShape.circle),
                  child: Center(
                    child: Text(
                      '${data.notificationsCount}',
                      style: const TextStyle(
                          color: AppColors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildProgressCard(DashboardData data) {
    final progress = data.learningProgress / 100;
    final l10n = AppLocalizations.of(context)!;

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
              // Circular progress ring
              SizedBox(
                width: 64,
                height: 64,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    SizedBox(
                      width: 64,
                      height: 64,
                      child: CircularProgressIndicator(
                        value: progress,
                        strokeWidth: 5,
                        backgroundColor: Colors.white.withValues(alpha: 0.25),
                        valueColor: const AlwaysStoppedAnimation(Colors.white),
                        strokeCap: StrokeCap.round,
                      ),
                    ),
                    Text(
                      '${data.learningProgress}%',
                      style: AppTextStyles.h4.copyWith(color: Colors.white),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.overallProgress,
                      style:
                          AppTextStyles.bodyBold.copyWith(color: Colors.white),
                    ),
                    const SizedBox(height: 4),
                    if (data.hasRoadmap)
                      Text(
                        '${data.roadmapResourcesCompleted} ${l10n.of_} ${data.roadmapResourcesTotal} ${l10n.resourcesCompleted}',
                        style: AppTextStyles.bodySmall
                            .copyWith(color: Colors.white70),
                      )
                    else
                      Text(
                        l10n.noRoadmapAvailable,
                        style: AppTextStyles.bodySmall
                            .copyWith(color: Colors.white70),
                      ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Progress bar
          ClipRRect(
            borderRadius: BorderRadius.circular(AppRadius.sm),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 6,
              backgroundColor: Colors.white.withValues(alpha: 0.25),
              valueColor: const AlwaysStoppedAnimation(Colors.white),
            ),
          ),
          const SizedBox(height: 14),
          // Stats row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Expanded(
                  child: _miniStat(
                '${data.skillsFound}',
                l10n.skillGrowth,
                Icons.star_outline,
              )),
              Expanded(
                  child: _miniStat(
                '${data.topicsCompleted}/${data.topicsTotal}',
                l10n.topics,
                Icons.topic_outlined,
              )),
              Expanded(
                  child: _miniStat(
                '${data.roadmapStepsCompleted}/${data.roadmapStepsTotal}',
                l10n.phases,
                Icons.route_outlined,
              )),
            ],
          ),
        ],
      ),
    );
  }

  Widget _miniStat(String value, String label, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: Colors.white70, size: 14),
        const SizedBox(width: 4),
        Flexible(
          child: Text(
            '$value $label',
            style: AppTextStyles.caption
                .copyWith(color: Colors.white70, fontSize: 11),
            overflow: TextOverflow.ellipsis,
            maxLines: 1,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActions(BuildContext context, DashboardData data) {
    final l10n = AppLocalizations.of(context)!;
    return Row(
      children: [
        Expanded(
            child: _ActionCard(
          icon: Icons.analytics_outlined,
          title: data.hasAnalysis ? l10n.newAnalysis : l10n.skillAnalysis,
          color: AppColors.primary,
          onTap: () => context.go(Routes.analysis),
        )),
        const SizedBox(width: AppSpacing.itemGap),
        Expanded(
            child: _ActionCard(
          icon:
              data.hasRoadmap ? Icons.play_circle_outline : Icons.map_outlined,
          title: data.hasRoadmap ? l10n.learningRoadmap : l10n.generateRoadmap,
          color: AppColors.accent,
          onTap: () => context.go(Routes.roadmap),
        )),
      ],
    );
  }

  /// Journey steps — clear visual of where the user is.
  Widget _buildJourneySteps(DashboardData data) {
    final l10n = AppLocalizations.of(context)!;
    final steps = [
      _JourneyStep(
        label: l10n.cvAnalyzed,
        icon: Icons.analytics_outlined,
        isDone: data.hasAnalysis,
        isActive: data.journeyStep == 'analyzed',
      ),
      _JourneyStep(
        label: l10n.roadmapReady,
        icon: Icons.map_outlined,
        isDone: data.hasRoadmap,
        isActive: data.journeyStep == 'roadmap_ready',
      ),
      _JourneyStep(
        label: l10n.learningStarted,
        icon: Icons.rocket_launch_outlined,
        isDone: data.learningProgress >= 100,
        isActive: data.journeyStep == 'learning',
      ),
    ];

    return VioraCard(
      color: AppColors.surfaceTinted,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(l10n.yourJourney,
              style: AppTextStyles.bodyBold.copyWith(color: AppColors.primary)),
          const SizedBox(height: 14),
          ...List.generate(steps.length, (i) {
            final step = steps[i];
            final isLast = i == steps.length - 1;
            return Column(
              children: [
                Row(
                  children: [
                    // Step indicator
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: step.isDone
                            ? AppColors.success
                            : step.isActive
                                ? AppColors.primary
                                : AppColors.surfaceVariant,
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: step.isDone
                            ? const Icon(Icons.check,
                                color: Colors.white, size: 16)
                            : step.isActive
                                ? const SizedBox(
                                    width: 14,
                                    height: 14,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.white,
                                    ),
                                  )
                                : Icon(step.icon,
                                    color: AppColors.textHint, size: 16),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        step.label,
                        style: AppTextStyles.body.copyWith(
                          color: step.isDone
                              ? AppColors.success
                              : step.isActive
                                  ? AppColors.primary
                                  : AppColors.textHint,
                          fontWeight: step.isActive
                              ? FontWeight.w600
                              : FontWeight.normal,
                        ),
                      ),
                    ),
                    if (step.isDone)
                      const Icon(Icons.check_circle,
                          size: 16, color: AppColors.success),
                  ],
                ),
                // Connector line
                if (!isLast)
                  Container(
                    margin: const EdgeInsetsDirectional.only(start: 15),
                    alignment: AlignmentDirectional.centerStart,
                    child: Container(
                      width: 2,
                      height: 28,
                      color: step.isDone
                          ? AppColors.success
                          : AppColors.outlineVariant,
                    ),
                  ),
              ],
            );
          }),
        ],
      ),
    );
  }
}

class _JourneyStep {
  final String label;
  final IconData icon;
  final bool isDone;
  final bool isActive;

  const _JourneyStep({
    required this.label,
    required this.icon,
    required this.isDone,
    required this.isActive,
  });
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color color;
  final VoidCallback onTap;

  const _ActionCard(
      {required this.icon,
      required this.title,
      required this.color,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return VioraCard(
      color: color.withValues(alpha: 0.04),
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
      borderColor: color.withValues(alpha: 0.15),
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(height: 10),
          Text(title,
              style: AppTextStyles.bodyBold.copyWith(color: color),
              textAlign: TextAlign.center),
        ],
      ),
    );
  }
}
