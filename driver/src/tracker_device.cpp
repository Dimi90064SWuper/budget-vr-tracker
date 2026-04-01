#include "tracker_device.h"
#include <cstdio>
#include <cstring>

CTrackerDevice::CTrackerDevice(const std::string& footSide, const std::string& serial)
    : m_sSerialNumber(serial), m_sFootSide(footSide) {
    memset(&m_currentPose, 0, sizeof(m_currentPose));
    m_currentPose.qWorldFromDriverRotation.w = 1.0f;
    m_currentPose.qDriverFromHeadRotation.w = 1.0f;
    printf("[BudgetVR] Tracker created: %s (%s)\n", serial.c_str(), footSide.c_str());
}

CTrackerDevice::~CTrackerDevice() { printf("[BudgetVR] Tracker destroyed: %s\n", m_sSerialNumber.c_str()); }

vr::EVRInitError CTrackerDevice::Activate(uint32_t unObjectId) {
    m_nObjectId = unObjectId;
    m_bIsActive = true;
    SetupProperties();
    m_bIsRegistered = true;
    return vr::VRInitError_None;
}

void CTrackerDevice::Deactivate() { m_bIsActive = false; m_bIsRegistered = false; }
void CTrackerDevice::EnterStandby() {}
void* CTrackerDevice::GetComponent(const char*) { return nullptr; }

void CTrackerDevice::DebugRequest(const char* pchRequest, char* pchResponseBuffer, uint32_t unResponseBufferSize) {
    if (pchRequest && pchResponseBuffer && unResponseBufferSize > 0)
        snprintf(pchResponseBuffer, unResponseBufferSize, "{\"serial\": \"%s\", \"active\": %s}",
                 m_sSerialNumber.c_str(), m_bIsActive ? "true" : "false");
}

vr::DriverPose_t CTrackerDevice::GetPose() {
    std::lock_guard<std::mutex> lock(m_poseMutex);
    return m_currentPose;
}

void CTrackerDevice::UpdatePose(const vr::HmdVector3_t& position, const vr::HmdQuaternion_t& rotation) {
    std::lock_guard<std::mutex> lock(m_poseMutex);
    if (!m_bIsActive) return;
    
    m_currentPose.vecPosition[0] = position.v[0];
    m_currentPose.vecPosition[1] = position.v[1];
    m_currentPose.vecPosition[2] = position.v[2];
    m_currentPose.qRotation = rotation;
    m_currentPose.poseIsValid = true;
    m_currentPose.deviceIsConnected = true;
    m_currentPose.result = vr::TrackingResult_Running_OK;
}

void CTrackerDevice::SetupProperties() {
    auto props = vr::VRProperties();
    if (!props) return;
    auto container = props->TrackedDeviceToPropertyContainer(m_nObjectId);
    
    props->SetStringProperty(container, vr::Prop_TrackingSystemName_String, "budget_vr_tracker");
    props->SetStringProperty(container, vr::Prop_ModelNumber_String, "budget_tracker");
    props->SetStringProperty(container, vr::Prop_SerialNumber_String, m_sSerialNumber.c_str());
    props->SetInt32Property(container, vr::Prop_DeviceClass_Int32, static_cast<int32_t>(vr::TrackedDeviceClass_GenericTracker));
    props->SetBoolProperty(container, vr::Prop_DeviceIsWireless_Bool, true);
    
    const char* role = (m_sFootSide == "left") ? "left_foot" : "right_foot";
    props->SetStringProperty(container, vr::Prop_AttachedDeviceId_String, role);
}
