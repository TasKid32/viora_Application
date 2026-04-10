import 'package:file_selector/file_selector.dart';

import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../shared/widgets/viora_page_header.dart';
import '../provider/analysis_provider.dart';

/// Upload section — file picker only (no manual skills input).
class UploadSection extends StatefulWidget {
  const UploadSection({super.key});

  @override
  State<UploadSection> createState() => _UploadSectionState();
}

class _UploadSectionState extends State<UploadSection> {
  String? _selectedFileName;
  String? _selectedFilePath;

  static const int _maxFileSizeBytes = 10 * 1024 * 1024; // 10MB
void _removeFile() {
  setState(() {
    _selectedFileName = null;
    _selectedFilePath = null;
  });
}

  Future<void> _pickFile() async {
  final XFile? file = await openFile(
    acceptedTypeGroups: [
      XTypeGroup(
        label: 'Documents',
        extensions: ['pdf', 'docx'],
      ),
    ],
  );

  if (file == null) return;

  final fileBytes = await file.length();

  // Validate file size (max 10MB)
  if (fileBytes > _maxFileSizeBytes) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            AppLocalizations.of(context)!
                .fileTooLarge((fileBytes / 1024 / 1024).toStringAsFixed(1)),
          ),
          backgroundColor: AppColors.error,
        ),
      );
    }
    return;
  }

  setState(() {
    _selectedFileName = file.name;
    _selectedFilePath = file.path;
  });
}


  void _startAnalysis() {
    final provider = context.read<AnalysisProvider>();

    // If previous analysis exists, warn user before re-analyzing
    if (provider.result != null) {
      final l10n = AppLocalizations.of(context)!;
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(l10n.reanalysisWarningTitle),
          content: Text(l10n.reanalysisWarningBody),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: Text(l10n.cancel),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(ctx);
                _doAnalysis(provider);
              },
              child: Text(l10n.continueText),
            ),
          ],
        ),
      );
      return;
    }

    _doAnalysis(provider);
  }

  void _doAnalysis(AnalysisProvider provider) {
    if (_selectedFilePath != null) {
      provider.analyzeFile(
        filePath: _selectedFilePath!,
        fileName: _selectedFileName!,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Unified page header
        VioraPageHeader(
          icon: Icons.cloud_upload_outlined,
          title: l10n.uploadCV,
        ),

        // Upload area
        GestureDetector(
          onTap: _pickFile,
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 32),
            decoration: BoxDecoration(
              color: _selectedFileName != null
                  ? AppColors.success.withValues(alpha: 0.04)
                  : AppColors.primarySurface,
              borderRadius: BorderRadius.circular(AppRadius.lg),
              border: Border.all(
                color: _selectedFileName != null
                    ? AppColors.success.withValues(alpha: 0.4)
                    : AppColors.primary.withValues(alpha: 0.2),
                width: 1.5,
              ),
            ),
            child: Column(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: _selectedFileName != null
                        ? AppColors.success.withValues(alpha: 0.1)
                        : AppColors.primarySurface,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _selectedFileName != null
                        ? Icons.check_circle
                        : Icons.cloud_upload_outlined,
                    size: 28,
                    color: _selectedFileName != null
                        ? AppColors.success
                        : AppColors.primary,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  _selectedFileName ?? l10n.tapToSelectFile,
                  style: AppTextStyles.bodyBold.copyWith(
                    color: _selectedFileName != null
                        ? AppColors.success
                        : AppColors.primary,
                  ),
                ),
                if (_selectedFileName == null) ...[
                  const SizedBox(height: 4),
                  Text(l10n.pdfDocxUpTo10, style: AppTextStyles.caption),
                ] else ...[
                  const SizedBox(height: 8),
                  TextButton.icon(
                    onPressed: _removeFile,
                    icon: const Icon(Icons.close,
                        size: 16, color: AppColors.error),
                    label: Text(l10n.removeFile,
                        style: AppTextStyles.caption
                            .copyWith(color: AppColors.error)),
                  ),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.sectionGap),

        // Analyze button
        Selector<AnalysisProvider, bool>(
          selector: (_, p) => p.isLoading,
          builder: (_, loading, __) {
            final canAnalyze = _selectedFilePath != null;
            return SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: (canAnalyze && !loading) ? _startAnalysis : null,
                icon: const Icon(Icons.analytics_outlined),
                label: Text(l10n.analyzeNow),
              ),
            );
          },
        ),

        // Error message
        Selector<AnalysisProvider, String?>(
          selector: (_, p) => p.error,
          builder: (_, error, __) {
            if (error == null) return const SizedBox.shrink();
            return Container(
              width: double.infinity,
              margin: const EdgeInsets.only(top: 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.error.withValues(alpha: 0.06),
                borderRadius: BorderRadius.circular(AppRadius.md),
                border:
                    Border.all(color: AppColors.error.withValues(alpha: 0.2)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline,
                      color: AppColors.error, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(error,
                        style: AppTextStyles.bodySmall
                            .copyWith(color: AppColors.error)),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}
