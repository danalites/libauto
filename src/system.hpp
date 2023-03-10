#pragma once

#include <atomic>
#include <chrono>
#include <functional>
#include <thread>

#include <uiohook.h>
#include "hook.h"

template <typename T> struct Callback;

template <typename Ret, typename... Params> struct Callback<Ret(Params...)> {
  template <typename... Args> static Ret callback(Args... args) {
    return func(args...);
  }
  static std::function<Ret(Params...)> func;
};

template <typename Ret, typename... Params>
std::function<Ret(Params...)> Callback<Ret(Params...)>::func;

// callback function pointer type
// https://stackoverflow.com/a/29817048
typedef void (*callback_t)(uiohook_event *const);

class System {
public:
  using py_callback_t = std::function<void(int)>;
  System() : t_(), py_cb_(), stop_(true) {}
  ~System() { stop(); }

  // return event of interest to python
  int e(int *k, int *j) {
    if (py_cb_) {
      py_cb_(*k);
    }
    return *k - *j;
  }

  void dispatch_process(uiohook_event *const event) {
    printf("Event@@@");
    // int status = hook_stop();
    if (py_cb_) {
      py_cb_(2222);
    }
  }

  bool start();
  bool start_event_loop();

  bool stop() {
    if (!t_.joinable())
      return false;
    stop_ = true;
    t_.join();
    return true;
  }

  bool registerCallback(py_callback_t cb) {
    if (t_.joinable())
      return false;
    py_cb_ = cb;
    return true;
  }

private:
  std::thread t_;
  py_callback_t py_cb_;
  std::atomic_bool stop_;
  std::unordered_map<int, int> eventTable;
};


bool System::start_event_loop() {
  Callback<void(uiohook_event *const)>::func =
      std::bind(&System::dispatch_process, this, std::placeholders::_1);
  callback_t func =
      static_cast<callback_t>(Callback<void(uiohook_event *const)>::callback);

  hook_event_loop(func);
  return true;
}

bool System::start() {
  if (t_.joinable())
    return false;
  stop_ = false;
  t_ = std::thread([this]() {
    while (!stop_) {
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
      if (py_cb_)
        py_cb_(1234);
    }
  });
  return true;
}