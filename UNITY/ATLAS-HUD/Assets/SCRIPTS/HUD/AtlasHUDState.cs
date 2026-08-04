/// <summary>
/// Ordered HUD state identifiers used by EnvironmentTransitionManager.
///
/// The normal forward journey follows ascending enum order:
///   AtlasFace → AISelectionHub → SpecialistWorkspace → ResearchArchive → CoreOperations
///
/// Back navigation and permitted direct jumps are also supported.
/// </summary>
public enum AtlasHUDState
{
    AtlasFace          = 0,
    AISelectionHub     = 1,
    SpecialistWorkspace = 2,
    ResearchArchive    = 3,
    CoreOperations     = 4,
}
