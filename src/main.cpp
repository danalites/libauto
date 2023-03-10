#include "pybind11/functional.h"
#include "system.hpp"
#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

int add(int i, int j) { return i + j; }

namespace py = pybind11;

PYBIND11_MODULE(iohook, m) {
  m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------
        .. currentmodule:: iohook
        .. autosummary::
           :toctree: _generate
           add
           subtract
    )pbdoc";

  m.def("add", &add, R"pbdoc(
        Add two numbers
        Some other explanation about the add function.
    )pbdoc");

  m.def(
      "subtract", [](int i, int j) { return i - j; }, R"pbdoc(
        Subtract two numbers
        Some other explanation about the subtract function.
    )pbdoc");

  py::class_<System>(m, "System")
      .def(py::init<>())
      .def("start", &System::start, py::call_guard<py::gil_scoped_release>())
      .def("start_event_loop", &System::start_event_loop,
           py::call_guard<py::gil_scoped_release>())
      .def("stop", &System::stop, py::call_guard<py::gil_scoped_release>())
      .def("registerCallback", &System::registerCallback);

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}