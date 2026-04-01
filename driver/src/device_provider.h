#ifndef BUDGET_VR_TRACKER_DEVICE_PROVIDER_H
#define BUDGET_VR_TRACKER_DEVICE_PROVIDER_H

#include <openvr_driver.h>
#include <memory>
#include <atomic>

class CControllerDevice;
class CTrackerDevice;
class UDPServer;

class CDeviceProvider : public vr::IServerTrackedDeviceProvider {
public:
    CDeviceProvider();
    virtual ~CDeviceProvider();

    virtual vr::EVRInitError Init(vr::IVRDriverContext* pDriverContext) override;
    virtual void Cleanup() override;
    virtual const char* const* GetInterfaceVersions() override;
    virtual void RunFrame() override;
    virtual bool ShouldBlockStandbyMode() override;
    virtual void EnterStandby() override;
    virtual void LeaveStandby() override;

    void OnFrame(const std::string& serial, const vr::HmdVector3_t& position,
                 const vr::HmdQuaternion_t& rotation, bool grip = false, float trigger = 0.0f);

    bool StartUDPServer(uint16_t port = 57011);
    void StopUDPServer();

private:
    vr::EVRInitError CreateDevices();
    void DestroyDevices();

private:
    CControllerDevice* m_pLeftController;
    CControllerDevice* m_pRightController;
    CTrackerDevice* m_pLeftFoot;
    CTrackerDevice* m_pRightFoot;
    std::unique_ptr<UDPServer> m_pUDPServer;
    std::atomic<bool> m_bRunning;
};

#endif
