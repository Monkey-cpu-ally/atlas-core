import 'package:flutter/material.dart';

import '../../domain/models/ui_prefs.dart';
import '../themes/skin_tokens.dart';
import '../widgets/hud_panels.dart';

class AppearanceLabOverlay extends StatelessWidget {
  const AppearanceLabOverlay({
    required this.visible,
    required this.skin,
    required this.prefs,
    required this.onExit,
    required this.onResetDefaults,
    required this.onPanelTiltChanged,
    required this.onFrameTypeChanged,
    required this.onFrameOpacityChanged,
    required this.onRingMaterialChanged,
    required this.onRingTransparencyChanged,
    required this.onRingLineWeightChanged,
    required this.onBackgroundChanged,
    required this.onAccentPreviewToggle,
    super.key,
  });

  final bool visible;
  final SkinTokens skin;
  final UiPrefs prefs;
  final VoidCallback onExit;
  final VoidCallback onResetDefaults;
  final ValueChanged<double> onPanelTiltChanged;
  final ValueChanged<String> onFrameTypeChanged;
  final ValueChanged<String> onFrameOpacityChanged;
  final ValueChanged<String> onRingMaterialChanged;
  final ValueChanged<double> onRingTransparencyChanged;
  final ValueChanged<double> onRingLineWeightChanged;
  final ValueChanged<String> onBackgroundChanged;
  final ValueChanged<bool> onAccentPreviewToggle;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      ignoring: !visible,
      child: AnimatedOpacity(
        opacity: visible ? 1 : 0,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
        child: Stack(
          children: [
            Positioned(
              top: 12,
              right: 12,
              child: ElevatedButton(
                onPressed: onExit,
                child: const Text('Exit'),
              ),
            ),
            Positioned(
              top: 76,
              left: 16,
              child: HudPanel(
                title: 'Left',
                skin: skin,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Panel tilt'),
                    Slider(
                      value: prefs.panelTiltDegrees,
                      min: 0,
                      max: 15,
                      onChanged: onPanelTiltChanged,
                    ),
                    DropdownButton<String>(
                      value: prefs.frameType,
                      isExpanded: true,
                      items: const [
                        DropdownMenuItem(value: 'none', child: Text('none')),
                        DropdownMenuItem(
                          value: 'hexagonalPlate',
                          child: Text('hexagonalPlate'),
                        ),
                        DropdownMenuItem(
                          value: 'circularPlate',
                          child: Text('circularPlate'),
                        ),
                        DropdownMenuItem(
                          value: 'angularTechFrame',
                          child: Text('angularTechFrame'),
                        ),
                        DropdownMenuItem(
                          value: 'organicSoftFrame',
                          child: Text('organicSoftFrame'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          onFrameTypeChanged(value);
                        }
                      },
                    ),
                    DropdownButton<String>(
                      value: prefs.frameOpacity,
                      isExpanded: true,
                      items: const [
                        DropdownMenuItem(value: 'solid', child: Text('solid')),
                        DropdownMenuItem(
                          value: 'semiTransparent',
                          child: Text('semiTransparent'),
                        ),
                        DropdownMenuItem(
                          value: 'outlineOnly',
                          child: Text('outlineOnly'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          onFrameOpacityChanged(value);
                        }
                      },
                    ),
                  ],
                ),
              ),
            ),
            Positioned(
              top: 76,
              right: 16,
              child: HudPanel(
                title: 'Right',
                skin: skin,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    DropdownButton<String>(
                      value: prefs.ringMaterial,
                      isExpanded: true,
                      items: const [
                        DropdownMenuItem(
                          value: 'solidMatte',
                          child: Text('solidMatte'),
                        ),
                        DropdownMenuItem(
                          value: 'frostedGlass',
                          child: Text('frostedGlass'),
                        ),
                        DropdownMenuItem(
                          value: 'transparentGlass',
                          child: Text('transparentGlass'),
                        ),
                        DropdownMenuItem(
                          value: 'lineOnlyMinimal',
                          child: Text('lineOnlyMinimal'),
                        ),
                        DropdownMenuItem(
                          value: 'mixedInnerSolidOuterTransparent',
                          child: Text('mixed'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          onRingMaterialChanged(value);
                        }
                      },
                    ),
                    const Text('Transparency'),
                    Slider(
                      value: prefs.ringTransparency,
                      min: 0,
                      max: 0.60,
                      onChanged: onRingTransparencyChanged,
                    ),
                    const Text('Line weight'),
                    Slider(
                      value: prefs.ringLineWeight,
                      min: 0.6,
                      max: 2.2,
                      onChanged: onRingLineWeightChanged,
                    ),
                  ],
                ),
              ),
            ),
            Positioned(
              left: 0,
              right: 0,
              bottom: 16,
              child: Center(
                child: SizedBox(
                  width: 620,
                  child: HudPanel(
                    title: 'Bottom',
                    skin: skin,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        DropdownButton<String>(
                          value: prefs.backgroundType,
                          isExpanded: true,
                          items: const [
                            DropdownMenuItem(
                              value: 'solidColor',
                              child: Text('solidColor'),
                            ),
                            DropdownMenuItem(
                              value: 'gradient',
                              child: Text('gradient'),
                            ),
                            DropdownMenuItem(
                              value: 'deepCosmicSpace',
                              child: Text('deepCosmicSpace'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value != null) {
                              onBackgroundChanged(value);
                            }
                          },
                        ),
                        SwitchListTile(
                          contentPadding: EdgeInsets.zero,
                          value: prefs.accentPreviewEnabled,
                          onChanged: onAccentPreviewToggle,
                          title: const Text('Accent preview toggle'),
                        ),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: OutlinedButton(
                            onPressed: onResetDefaults,
                            child: const Text('Reset to Default'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

