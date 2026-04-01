#include <openvr_driver.h>
#include <cstring>
#include "device_provider.h"

#if defined(_WIN32)
    #define HMD_EXPORT __declspec(dllexport)
#else
    #define HMD_EXPORT __attribute__((visibility("default")))
#endif

static CDeviceProvider* g_pProvider = nullptr;

HMD_EXPORT void* HmdSystemFactory(const char* pchInterfaceName, int* pReturnVersion) {
    if (std::strcmp(pchInterfaceName, vr::IServerTrackedDeviceProvider_Version) == 0) {
        if (!g_pProvider) g_pProvider = new CDeviceProvider();
        return static_cast<vr::IServerTrackedDeviceProvider*>(g_pProvider);
    }
    return nullptr;
}

HMD_EXPORT void CleanupDriver() {
    if (g_pProvider) { delete g_pProvider; g_pProvider = nullptr; }
}
