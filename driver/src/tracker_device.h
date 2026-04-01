#ifndef TRACKER_DEVICE_H
#define TRACKER_DEVICE_H

#include <openvr_driver.h>
#include <string>
#include <atomic>
#include <mutex>

class CTrackerDevice : public vr::ITrackedDeviceServerDriver {
public:
    explicit CTrackerDevice(const std::string& footSide, const std::string& serial);
    virtual ~CTrackerDevice();
    
    virtual vr::EVRInitError Activate(uint32_t unObjectId) override;
    virtual void Deactivate() override;
    virtual void EnterStandby() override;
    virtual void* GetComponent(const char* pchComponentNameAndVersion) override;
    virtual void DebugRequest(const char* pchRequest, char* pchResponseBuffer, uint32_t unResponseBufferSize) override;
    virtual vr::DriverPose_t GetPose() override;
    
    void UpdatePose(const vr::HmdVector3_t& position, const vr::HmdQuaternion_t& rotation);
    bool IsActive() const { return m_bIsActive; }

private:
    void SetupProperties();

private:
    uint32_t m_nObjectId = 0;
    std::string m_sSerialNumber, m_sFootSide;
    std::atomic<bool> m_bIsActive = false;
    bool m_bIsRegistered = false;
    vr::DriverPose_t m_currentPose{};
    std::mutex m_poseMutex;
};

#endif
