#include "device_provider.h"
#include "controller_device.h"
#include "tracker_device.h"
#include "pipe_server.h"
#include <cstdio>
#include <nlohmann/json.hpp>

static const char* k_InterfaceVersions[] = {vr::IServerTrackedDeviceProvider_Version, nullptr};

CDeviceProvider::CDeviceProvider()
    : m_pLeftController(nullptr), m_pRightController(nullptr)
    , m_pLeftFoot(nullptr), m_pRightFoot(nullptr)
    , m_pUDPServer(nullptr), m_bRunning(false) {}

CDeviceProvider::~CDeviceProvider() { Cleanup(); }

vr::EVRInitError CDeviceProvider::Init(vr::IVRDriverContext*) {
    printf("[BudgetVR] Initializing...\n");
    vr::VR_Init(nullptr);
    CreateDevices();
    StartUDPServer(57011);
    m_bRunning = true;
    return vr::VRInitError_None;
}

void CDeviceProvider::Cleanup() {
    m_bRunning = false;
    StopUDPServer();
    DestroyDevices();
    vr::VR_Shutdown();
}

const char* const* CDeviceProvider::GetInterfaceVersions() { return k_InterfaceVersions; }
void CDeviceProvider::RunFrame() {}
bool CDeviceProvider::ShouldBlockStandbyMode() { return false; }
void CDeviceProvider::EnterStandby() {}
void CDeviceProvider::LeaveStandby() {}

vr::EVRInitError CDeviceProvider::CreateDevices() {
    m_pLeftController = new CControllerDevice("left", "budget_vr_left_ctrl");
    vr::VRServerDriverHost()->TrackedDeviceAdded("budget_vr_left_ctrl", vr::TrackedDeviceClass_Controller, m_pLeftController);
    
    m_pRightController = new CControllerDevice("right", "budget_vr_right_ctrl");
    vr::VRServerDriverHost()->TrackedDeviceAdded("budget_vr_right_ctrl", vr::TrackedDeviceClass_Controller, m_pRightController);
    
    m_pLeftFoot = new CTrackerDevice("left", "budget_vr_left_foot");
    vr::VRServerDriverHost()->TrackedDeviceAdded("budget_vr_left_foot", vr::TrackedDeviceClass_GenericTracker, m_pLeftFoot);
    
    m_pRightFoot = new CTrackerDevice("right", "budget_vr_right_foot");
    vr::VRServerDriverHost()->TrackedDeviceAdded("budget_vr_right_foot", vr::TrackedDeviceClass_GenericTracker, m_pRightFoot);
    
    printf("[BudgetVR] 4 devices created\n");
    return vr::VRInitError_None;
}

void CDeviceProvider::DestroyDevices() {
    delete m_pLeftController; delete m_pRightController;
    delete m_pLeftFoot; delete m_pRightFoot;
}

void CDeviceProvider::OnFrame(const std::string& serial, const vr::HmdVector3_t& pos,
                               const vr::HmdQuaternion_t& rot, bool grip, float trigger) {
    if (serial == "budget_vr_left_ctrl" && m_pLeftController)
        m_pLeftController->UpdatePose(pos, rot, grip, trigger);
    else if (serial == "budget_vr_right_ctrl" && m_pRightController)
        m_pRightController->UpdatePose(pos, rot, grip, trigger);
    else if (serial == "budget_vr_left_foot" && m_pLeftFoot)
        m_pLeftFoot->UpdatePose(pos, rot);
    else if (serial == "budget_vr_right_foot" && m_pRightFoot)
        m_pRightFoot->UpdatePose(pos, rot);
}

bool CDeviceProvider::StartUDPServer(uint16_t port) {
    if (m_pUDPServer) StopUDPServer();
    m_pUDPServer = std::make_unique<UDPServer>(this, port);
    return m_pUDPServer->Start();
}

void CDeviceProvider::StopUDPServer() {
    if (m_pUDPServer) { m_pUDPServer->Stop(); m_pUDPServer.reset(); }
}
