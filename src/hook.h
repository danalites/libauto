#ifndef H_HOOK
#define H_HOOK

#ifdef __cplusplus
extern "C" {
#endif

int hook_event_loop(void (*func)(uiohook_event *const));

#ifdef __cplusplus
}
#endif

#endif /* H_HOOK */