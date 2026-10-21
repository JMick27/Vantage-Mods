#include <stdint.h>
#include <string.h>
#include <windows.h>

#define VANTAGE_ENGINE_RUNTIME_ABI 1u
#define VANTAGE_EXPORT __declspec(dllexport)

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved) {
    (void)instance; (void)reason; (void)reserved;
    return TRUE;
}

VANTAGE_EXPORT uint32_t VantageEngineRuntime_GetAbiVersion(void) {
    return VANTAGE_ENGINE_RUNTIME_ABI;
}

VANTAGE_EXPORT const char *VantageEngineRuntime_GetEngineId(void) {
    return "unreal";
}

VANTAGE_EXPORT uint32_t VantageEngineRuntime_GetCapabilities(void) {
    return 0u;
}

VANTAGE_EXPORT int VantageEngineRuntime_ValidateModuleContract(const char *contract) {
    if (contract == NULL || contract[0] == '\0') return 10;
    if (strstr(contract, "vantage-unreal-game-module") == NULL) return 11;
    if (strstr(contract, "exactBuildRequired") == NULL) return 12;
    return 0;
}
