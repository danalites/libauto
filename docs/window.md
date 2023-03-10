### Mouse keyboard emulation
- How to distinguish between global and local mouse events? 

- Global actions can be used to move the window, or click non-window buttons (e.g., docks or start button). Local is easier for locating window-specific buttons.
  
- Interventions: multiple global mouse/keyboard will always conflict.

```yaml

actions:
    # mouse/keyboard actions inside window 
    - window.active():
        - mouse.move({{ (100,100) }} )
        - mouse.click()
    
    # mouse/keyboard actions outside window (global)
    mouse.move({{ (100,100) }} )

```
