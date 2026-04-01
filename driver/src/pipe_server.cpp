#include "pipe_server.h"
#include "device_provider.h"
#include <cstdio>
#include <cstring>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

#ifdef _WIN32
    #define SOCKET_INVALID INVALID_SOCKET
    #define SOCKET_ERROR_CODE SOCKET_ERROR
#else
    #define SOCKET_INVALID -1
    #define SOCKET_ERROR_CODE -1
#endif

UDPServer::UDPServer(CDeviceProvider* provider, uint16_t port)
    : m_pProvider(provider), m_nPort(port), m_socket(SOCKET_INVALID), m_bRunning(false) {
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
    memset(m_buffer, 0, BUFFER_SIZE);
}

UDPServer::~UDPServer() {
    Stop();
#ifdef _WIN32
    WSACleanup();
#endif
}

bool UDPServer::Start() {
    if (m_bRunning) return true;
    if (!InitializeSocket()) return false;
    m_bRunning = true;
    m_pThread = std::make_unique<std::thread>(&UDPServer::Run, this);
    printf("[BudgetVR] UDP server started on port %u\n", m_nPort);
    return true;
}

void UDPServer::Stop() {
    if (!m_bRunning) return;
    m_bRunning = false;
    if (m_pThread && m_pThread->joinable()) m_pThread->join();
    CloseSocket();
}

bool UDPServer::InitializeSocket() {
#ifdef _WIN32
    m_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
#else
    m_socket = socket(AF_INET, SOCK_DGRAM, 0);
#endif
    if (m_socket == SOCKET_INVALID) return false;
    
    int reuse = 1;
#ifdef _WIN32
    setsockopt(m_socket, SOL_SOCKET, SO_REUSEADDR, (const char*)&reuse, sizeof(reuse));
#else
    setsockopt(m_socket, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#endif
    
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(m_nPort);
    
    if (bind(m_socket, (sockaddr*)&addr, sizeof(addr)) == SOCKET_ERROR_CODE) {
        CloseSocket();
        return false;
    }
    return true;
}

void UDPServer::CloseSocket() {
    if (m_socket != SOCKET_INVALID) {
#ifdef _WIN32
        closesocket(m_socket);
#else
        close(m_socket);
#endif
        m_socket = SOCKET_INVALID;
    }
}

void UDPServer::Run() {
    sockaddr_in clientAddr{};
    socklen_t clientLen = sizeof(clientAddr);
    
    while (m_bRunning) {
        int bytesReceived = recvfrom(m_socket, m_buffer, BUFFER_SIZE - 1, 0,
                                      (sockaddr*)&clientAddr, &clientLen);
        
        if (bytesReceived == SOCKET_ERROR_CODE) continue;
        if (bytesReceived > 0) {
            m_buffer[bytesReceived] = '\0';
            HandleMessage(m_buffer, static_cast<size_t>(bytesReceived));
        }
    }
}

void UDPServer::HandleMessage(const char* data, size_t length) {
    try {
        json j = json::parse(data, data + length);
        if (!j.contains("devices") || !j["devices"].is_object()) return;
        
        auto& devices = j["devices"];
        
        if (devices.contains("left_ctrl")) {
            auto& dev = devices["left_ctrl"];
            vr::HmdVector3_t pos = {(float)dev["pos"][0], (float)dev["pos"][1], (float)dev["pos"][2]};
            vr::HmdQuaternion_t rot = {(double)dev["rot"][0], (double)dev["rot"][1], (double)dev["rot"][2], (double)dev["rot"][3]};
            bool grip = dev.value("buttons", json::object()).value("grip", false);
            float trigger = dev.value("buttons", json::object()).value("trigger", 0.0f);
            m_pProvider->OnFrame("budget_vr_left_ctrl", pos, rot, grip, trigger);
        }
        if (devices.contains("right_ctrl")) {
            auto& dev = devices["right_ctrl"];
            vr::HmdVector3_t pos = {(float)dev["pos"][0], (float)dev["pos"][1], (float)dev["pos"][2]};
            vr::HmdQuaternion_t rot = {(double)dev["rot"][0], (double)dev["rot"][1], (double)dev["rot"][2], (double)dev["rot"][3]};
            bool grip = dev.value("buttons", json::object()).value("grip", false);
            float trigger = dev.value("buttons", json::object()).value("trigger", 0.0f);
            m_pProvider->OnFrame("budget_vr_right_ctrl", pos, rot, grip, trigger);
        }
        if (devices.contains("left_foot")) {
            auto& dev = devices["left_foot"];
            vr::HmdVector3_t pos = {(float)dev["pos"][0], (float)dev["pos"][1], (float)dev["pos"][2]};
            vr::HmdQuaternion_t rot = {(double)dev["rot"][0], (double)dev["rot"][1], (double)dev["rot"][2], (double)dev["rot"][3]};
            m_pProvider->OnFrame("budget_vr_left_foot", pos, rot);
        }
        if (devices.contains("right_foot")) {
            auto& dev = devices["right_foot"];
            vr::HmdVector3_t pos = {(float)dev["pos"][0], (float)dev["pos"][1], (float)dev["pos"][2]};
            vr::HmdQuaternion_t rot = {(double)dev["rot"][0], (double)dev["rot"][1], (double)dev["rot"][2], (double)dev["rot"][3]};
            m_pProvider->OnFrame("budget_vr_right_foot", pos, rot);
        }
    } catch (const std::exception& e) {
        printf("[BudgetVR] JSON parse error: %s\n", e.what());
    }
}
