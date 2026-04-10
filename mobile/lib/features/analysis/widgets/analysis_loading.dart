import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../provider/analysis_provider.dart';

/// 4-step loading overlay — shows real-time progress through the analysis pipeline.
///
/// Steps:
/// 1. Uploading file (with real % progress)
/// 2. Extracting text from document
/// 3. Analyzing skills with AI (NER model)
/// 4. Matching with career database (O*NET)
class AnalysisLoading extends StatelessWidget {
  const AnalysisLoading({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withValues(alpha: 0.5),
      child: Center(
        child: Container(
          margin: const EdgeInsets.all(24),
          padding: const EdgeInsets.all(28),
          decoration: BoxDecoration(
            color: AppColors.white,
            borderRadius: BorderRadius.circular(AppRadius.xl),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withValues(alpha: 0.15),
                blurRadius: 30,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Animated icon with brand gradient ring
              const _PulsingIcon(),
              const SizedBox(height: 20),

              // Stage title
              Selector<AnalysisProvider, AnalysisStage>(
                selector: (_, p) => p.stage,
                builder: (_, stage, __) {
                  return Text(
                    _stageTitle(stage, AppLocalizations.of(context)!),
                    style: AppTextStyles.h3.copyWith(color: AppColors.primary),
                    textAlign: TextAlign.center,
                  );
                },
              ),
              const SizedBox(height: 6),

              // Stage description
              Selector<AnalysisProvider, AnalysisStage>(
                selector: (_, p) => p.stage,
                builder: (_, stage, __) {
                  return Text(
                    _stageDescription(stage, AppLocalizations.of(context)!),
                    style: AppTextStyles.body.copyWith(
                      color: AppColors.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  );
                },
              ),
              const SizedBox(height: 20),

              // Real progress bar (upload) or indeterminate (other stages)
              Selector<AnalysisProvider, double>(
                selector: (_, p) => p.uploadProgress,
                builder: (_, progress, __) {
                  final stage = context.read<AnalysisProvider>().stage;
                  if (stage == AnalysisStage.uploading) {
                    return Column(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(AppRadius.sm),
                          child: LinearProgressIndicator(
                            value: progress,
                            minHeight: 8,
                            backgroundColor: AppColors.primaryContainer,
                            valueColor:
                                const AlwaysStoppedAnimation(AppColors.primary),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${(progress * 100).toInt()}%',
                          style: AppTextStyles.bodyBold
                              .copyWith(color: AppColors.primary),
                        ),
                      ],
                    );
                  }
                  return ClipRRect(
                    borderRadius: BorderRadius.circular(AppRadius.sm),
                    child: const LinearProgressIndicator(
                      minHeight: 8,
                      backgroundColor: AppColors.primaryContainer,
                      valueColor: AlwaysStoppedAnimation(AppColors.primary),
                    ),
                  );
                },
              ),

              const SizedBox(height: 20),

              // 4-step indicator
              Selector<AnalysisProvider, AnalysisStage>(
                selector: (_, p) => p.stage,
                builder: (_, currentStage, __) {
                  final l10n = AppLocalizations.of(context)!;
                  return Column(
                    children: [
                      _buildStep(
                        Icons.cloud_upload_outlined,
                        l10n.uploadFile,
                        stepStage: AnalysisStage.uploading,
                        currentStage: currentStage,
                      ),
                      const SizedBox(height: 10),
                      _buildStep(
                        Icons.description_outlined,
                        l10n.extractText,
                        stepStage: AnalysisStage.extracting,
                        currentStage: currentStage,
                      ),
                      const SizedBox(height: 10),
                      _buildStep(
                        Icons.psychology_outlined,
                        l10n.aiSkillAnalysis,
                        stepStage: AnalysisStage.analyzing,
                        currentStage: currentStage,
                      ),
                      const SizedBox(height: 10),
                      _buildStep(
                        Icons.compare_arrows_outlined,
                        l10n.careerMatching,
                        stepStage: AnalysisStage.matching,
                        currentStage: currentStage,
                      ),
                    ],
                  );
                },
              ),

              const SizedBox(height: 16),

              // Estimated time
              Text(
                AppLocalizations.of(context)!.usuallyTakes,
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textHint,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Get the stage order index for comparison.
  static int _stageIndex(AnalysisStage stage) {
    switch (stage) {
      case AnalysisStage.uploading:
        return 0;
      case AnalysisStage.extracting:
        return 1;
      case AnalysisStage.analyzing:
        return 2;
      case AnalysisStage.matching:
        return 3;
      case AnalysisStage.complete:
        return 4;
      default:
        return -1;
    }
  }

  String _stageTitle(AnalysisStage stage, AppLocalizations l10n) {
    switch (stage) {
      case AnalysisStage.uploading:
        return l10n.uploadingResume;
      case AnalysisStage.extracting:
        return l10n.extractingText;
      case AnalysisStage.analyzing:
        return l10n.aiSkillAnalysis;
      case AnalysisStage.matching:
        return l10n.careerMatching;
      default:
        return l10n.processing;
    }
  }

  String _stageDescription(AnalysisStage stage, AppLocalizations l10n) {
    switch (stage) {
      case AnalysisStage.uploading:
        return l10n.uploadingDesc;
      case AnalysisStage.extracting:
        return l10n.extractingDesc;
      case AnalysisStage.analyzing:
        return l10n.analyzingDesc;
      case AnalysisStage.matching:
        return l10n.matchingDesc;
      default:
        return l10n.processingDesc;
    }
  }

  Widget _buildStep(
    IconData icon,
    String label, {
    required AnalysisStage stepStage,
    required AnalysisStage currentStage,
  }) {
    final stepIdx = _stageIndex(stepStage);
    final currentIdx = _stageIndex(currentStage);
    final isDone = currentIdx > stepIdx;
    final isActive = currentIdx == stepIdx;

    return Row(
      children: [
        // Circle indicator
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: isDone
                ? AppColors.success
                : (isActive ? AppColors.primary : AppColors.primarySurface),
            shape: BoxShape.circle,
            boxShadow: isActive
                ? [
                    BoxShadow(
                      color: AppColors.primary.withValues(alpha: 0.3),
                      blurRadius: 8,
                    ),
                  ]
                : null,
          ),
          child: Icon(
            isDone ? Icons.check : icon,
            size: 16,
            color: (isDone || isActive) ? AppColors.white : AppColors.primary,
          ),
        ),
        const SizedBox(width: 12),
        // Label
        Expanded(
          child: Text(
            label,
            style: AppTextStyles.body.copyWith(
              color: isDone
                  ? AppColors.success
                  : (isActive ? AppColors.textPrimary : AppColors.textHint),
              fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ),
        // Status indicator
        if (isDone)
          const Icon(Icons.check_circle, size: 18, color: AppColors.success)
        else if (isActive)
          SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: AppColors.primary,
            ),
          ),
      ],
    );
  }
}

/// Pulsing animation for loading icon — brand-colored ring.
class _PulsingIcon extends StatefulWidget {
  const _PulsingIcon();

  @override
  State<_PulsingIcon> createState() => _PulsingIconState();
}

class _PulsingIconState extends State<_PulsingIcon>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      child: const Icon(
        Icons.analytics_outlined,
        color: AppColors.primary,
        size: 32,
      ),
      builder: (_, child) => Transform.scale(
        scale: 0.9 + (_ctrl.value * 0.2),
        child: Container(
          width: 64,
          height: 64,
          decoration: BoxDecoration(
            color: AppColors.primaryContainer,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withValues(
                  alpha: 0.15 + _ctrl.value * 0.15,
                ),
                blurRadius: 20,
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
