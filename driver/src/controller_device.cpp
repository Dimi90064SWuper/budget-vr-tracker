#include "controller_device.h"
#include <cstdio>
#include <cstring>

CControllerDevice::CControllerDevice(const std::string& handSide, const std::string& serial)
    : m_sSerialNumber(serial), m_sHandSide(handSide) {
    memset(&m_currentPose, 0, sizeof(m_currentPose));
    m_currentPose.qWorldFromDriverRotation.w = 1.0f;
    m_currentPose.qDriverFromHeadRotation.w = 1.0f;
    printf("[BudgetVR] Controller created: %s (%s)\n", serial.c_str(), handSide.c_str());
}

CControllerDevice::~CControllerDevice() { printf("[BudgetVR] Controller destroyed: %s\n", m_sSerialNumber.c_str()); }

vr::EVRInitError CControllerDevice::Activate(uint32_t unObjectId) {
    m_nObjectId = unObjectId;
    m_bIsActive = true;
    SetupProperties();
    CreateInputComponents();
    m_bIsRegistered = true;
    return vr::VRInitError_None;
}

void CControllerDevice::Deactivate() { m_bIsActive = false; m_bIsRegistered = false; }
void CControllerDevice::EnterStandby() {}
void* CControllerDevice::GetComponent(const char*) { return nullptr; }

void CControllerDevice::DebugRequest(const char* pchRequest, char* pchResponseBuffer, uint32_t unResponseBufferSize) {
    if (pchRequest && pchResponseBuffer && unResponseBufferSize > 0)
        snprintf(pchResponseBuffer, unResponseBufferSize, "{\"serial\": \"%s\", \"active\": %s}",
                 m_sSerialNumber.c_str(), m_bIsActive ? "true" : "false");
}

vr::DriverPose_t CControllerDevice::GetPose() {
    std::lock_guard<std::mutex> lock(m_poseMutex);
    return m_currentPose;
}

void CControllerDevice::UpdatePose(const vr::HmdVector3_t& position, const vr::HmdQuaternion_t& rotation,
                                    bool grip, float trigger) {
    std::lock_guard<std::mutex> lock(m_poseMutex);
    if (!m_bIsActive) return;
    
    m_currentPose.vecPosition[0] = position.v[0];
    m_currentPose.vecPosition[1] = position.v[1];
    m_currentPose.vecPosition[2] = position.v[2];
    m_currentPose.qRotation = rotation;
    m_currentPose.poseIsValid = true;
    m_currentPose.deviceIsConnected = true;
    m_currentPose.result = vr::TrackingResult_Running_OK;
    
    if (m_gripHandle != vr::k_ulInvalidInputComponentHandle)
        vr::VRDriverInput()->UpdateBooleanComponent(m_gripHandle, grip, 0);
    if (m_triggerHandle != vr::k_ulInvalidInputComponentHandle)
        vr::VRDriverInput()->UpdateScalarComponent(m_triggerHandle, trigger, 0);
}

void CControllerDevice::SetupProperties() {
    auto props = vr::VRProperties();
    if (!props) return;
    auto container = props->TrackedDeviceToPropertyContainer(m_nObjectId);
    
    uint32_t role = (m_sHandSide == "left") ? 1 : 2;
    props->SetStringProperty(container, vr::Prop_TrackingSystemName_String, "budget_vr_tracker");
    props->SetStringProperty(container, vr::Prop_ModelNumber_String, "budget_controller");
    props->SetStringProperty(container, vr::Prop_SerialNumber_String, m_sSerialNumber.c_str());
    props->SetInt32Property(container, vr::Prop_ControllerRoleHint_Int32, role);
    props->SetBoolProperty(container, vr::Prop_DeviceIsWireless_Bool, true);
}

void CControllerDevice::CreateInputComponents() {
    auto props = vr::VRProperties();
    if (!props) return;
    auto container = props->TrackedDeviceToPropertyContainer(m_nObjectId);
    
    vr::VRDriverInput()->CreateBooleanComponent(container, "/input/grip/click", &m_gripHandle);
    vr::VRDriverInput()->CreateScalarComponent(container, "/input/trigger/value", &m_triggerHandle,
                                                vr::VRScalarType_Absolute, vr::VRScalarUnits_NormalizedOneSided);
    vr::VRDriverInput()->CreateHapticComponent(container, "/output/haptic", &m_hapticHandle);
}
