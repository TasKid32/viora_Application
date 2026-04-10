import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../provider/analysis_provider.dart';
import '../widgets/upload_section.dart';
import '../widgets/analysis_loading.dart';
import '../widgets/results_section.dart';

/// Analysis screen — composed of small widgets.
///
/// Two states:
/// - Pre-analysis: full upload section
/// - Post-analysis: compact file summary + structured results
class AnalysisScreen extends StatelessWidget {
  const AnalysisScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.skillAnalysisTitle),
      ),
      body: Stack(
        children: [
          // Main content — switches between upload and results
          Selector<AnalysisProvider, AnalysisStage>(
            selector: (_, p) => p.stage,
            builder: (_, stage, __) {
              if (stage == AnalysisStage.complete) {
                // Post-analysis: compact summary + results
                return SingleChildScrollView(
                  padding: AppSpacing.screenPadding,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      _CompactFileSummary(),
                      SizedBox(height: 16),
                      ResultsSection(),
                    ],
                  ),
                );
              }

              // Pre-analysis: full upload section
              return SingleChildScrollView(
                padding: AppSpacing.screenPadding,
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    UploadSection(),
                  ],
                ),
              );
            },
          ),

          // Loading overlay
          Selector<AnalysisProvider, bool>(
            selector: (_, p) => p.isLoading,
            builder: (_, loading, __) {
              if (!loading) return const SizedBox.shrink();
              return const AnalysisLoading();
            },
          ),
        ],
      ),
    );
  }
}

/// Compact file summary — replaces the large upload area after analysis.
///
/// Shows: success status + predicted job + action to re-analyze.
class _CompactFileSummary extends StatelessWidget {
  const _CompactFileSummary();

  @override
  Widget build(BuildContext context) {
    final provider = context.read<AnalysisProvider>();
    final result = provider.result;
    final l10n = AppLocalizations.of(context)!;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.surfaceTinted,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.12)),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.success.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.check_circle,
                color: AppColors.success, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(l10n.analysisComplete, style: AppTextStyles.bodyBold),
                if (result != null)
                  Text(
                    result.predictedJob,
                    style: AppTextStyles.caption
                        .copyWith(color: AppColors.textSecondary),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
              ],
            ),
          ),
          // Re-analyze action
          TextButton.icon(
            onPressed: () => provider.reset(),
            icon: const Icon(Icons.refresh, size: 16),
            label: Text(l10n.retry, style: AppTextStyles.caption),
            style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
          ),
        ],
      ),
    );
  }
}
