#ifndef PIPE_SERVER_H
#define PIPE_SERVER_H

#include <atomic>
#include <memory>
#include <thread>
#include <cstdint>

#ifdef _WIN32
    #include <winsock2.h>
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
#endif

class CDeviceProvider;

class UDPServer {
public:
    explicit UDPServer(CDeviceProvider* provider, uint16_t port = 57011);
    ~UDPServer();
    bool Start();
    void Stop();
    bool IsRunning() const { return m_bRunning; }

private:
    void Run();
    void HandleMessage(const char* data, size_t length);
    bool InitializeSocket();
    void CloseSocket();

private:
    CDeviceProvider* m_pProvider;
    uint16_t m_nPort;
#ifdef _WIN32
    SOCKET m_socket;
#else
    int m_socket;
#endif
    std::atomic<bool> m_bRunning;
    std::unique_ptr<std::thread> m_pThread;
    static constexpr size_t BUFFER_SIZE = 4096;
    char m_buffer[BUFFER_SIZE];
};

#endif
