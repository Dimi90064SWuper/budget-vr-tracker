#ifndef CONTROLLER_DEVICE_H
#define CONTROLLER_DEVICE_H

#include <openvr_driver.h>
#include <string>
#include <atomic>
#include <mutex>

class CControllerDevice : public vr::ITrackedDeviceServerDriver {
public:
    explicit CControllerDevice(const std::string& handSide, const std::string& serial);
    virtual ~CControllerDevice();
    
    virtual vr::EVRInitError Activate(uint32_t unObjectId) override;
    virtual void Deactivate() override;
    virtual void EnterStandby() override;
    virtual void* GetComponent(const char* pchComponentNameAndVersion) override;
    virtual void DebugRequest(const char* pchRequest, char* pchResponseBuffer, uint32_t unResponseBufferSize) override;
    virtual vr::DriverPose_t GetPose() override;
    
    void UpdatePose(const vr::HmdVector3_t& position, const vr::HmdQuaternion_t& rotation,
                    bool grip = false, float trigger = 0.0f);
    bool IsActive() const { return m_bIsActive; }

private:
    void SetupProperties();
    void CreateInputComponents();

private:
    uint32_t m_nObjectId = 0;
    std::string m_sSerialNumber, m_sHandSide;
    std::atomic<bool> m_bIsActive = false;
    bool m_bIsRegistered = false;
    vr::DriverPose_t m_currentPose{};
    std::mutex m_poseMutex;
    vr::VRInputComponentHandle_t m_gripHandle = vr::k_ulInvalidInputComponentHandle;
    vr::VRInputComponentHandle_t m_triggerHandle = vr::k_ulInvalidInputComponentHandle;
    vr::VRInputComponentHandle_t m_hapticHandle = vr::k_ulInvalidInputComponentHandle;
};

#endif
