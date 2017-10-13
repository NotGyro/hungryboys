import pygame, sys
from pygame.locals import *

# None of this code is particularly optimized yet - currently, it relies heavily on strings.
# I can fix that later if we need to but input code usually isn't a bottleneck.


# @todo TODO: Error handling for basically everything in here. 

## Up / down state for action codes.
class ActionState:
    PRESSED, RELEASED = range(2)

## An InputContext represents the different situations in which one can input. Examples: Game, menu, etc.
# The InputContext translates keypresses into game actions - it makes keys remappable.
# Keys are mapped to an "Action name," somewhat like a virtual keycode that refers to an action in gameplay.
class InputContext:

    ## Initializes an InputContext, passing the name as an argument.
    # Example: InputContext("Menu"), InputContext("Game"), InputContext("ChatBar").
    # Naming convention is UpperSnakeCase
    def __init__(self, n, passkeys=False): 
        self.name = n

        # Initialize a dictionary of mappings of keycode to action name
        # This only has so much stuff in it for testing reasons, presently.
        self.keymap = { "up" : "MoveUp", "right" : "MoveRight", "down" : "MoveDown", "left" : "MoveLeft" }

        # Initialize a list of which action('s buttons) are held down at the moment.
        self.actions_down = []

        # A handy-dandy debug switch.
        self.debug_input = False

        # The passthrough flag. If this is set to true, all keys not registered to actions
        # will be sent along (via a to be determined method) to another class as text -
        # this is the "type in your name" state.
        self.passthrough = passkeys # Defaults to false.

        # For use with passthrough. Are we currently typing capital letters?
        self.caps = False

    def handle_event(self, event):
        # @todo TODO: Joystick / controller / mouse support.
        if event.type == pygame.KEYDOWN:
            self.handle_keycode(pygame.key.name(event.key), True)
        elif event.type == pygame.KEYUP:
            self.handle_keycode(pygame.key.name(event.key), False)

    ## Called by handle_event and by attach. The meat of the key handing functionality.
    def handle_keycode(self, key, down):
        if self.debug_input==True:
            if down == True:
                state_print = "Down"
            elif down == False:
                state_print = "Up"
            print("Key pressed in InputContext: " + key)
            print("Key state is now: " + state_print)
        if(key in self.keymap):
            if self.debug_input==True:
                print("Action code " + self.keymap[key] + " detected")


    ## Called when this context becomes active.
    def attach(self, current_down=[]):
        for key in current_down:
            self.handle_keycode(key, True);


    ## Called when this context is no longer active.
    def detach(self):
        del self.actions_down[:] # Clear keys-down list.
        self.caps = False



## InputManager is the meta-InputContext. It's a black box you can shove input into and it will work.
# This remaps key-presses into action codes.
# Keys are mapped to an "Action name," somewhat like a virtual keycode that refers to an action in gameplay.
class InputManager():
    def __init__(self): 
        # Input debug switch. Copies to contexts.
        self.debug_input = True

        # This variable represents our current context.
        self.context = InputContext("default")
        self.contexts = { "default" : self.context }
        # Make sure this propagates.
        self.context.debug_input = self.debug_input

        # A master list of which keys are held down presently.
        # This is kept separate from a context.actions_down, in order to avoid shenanigans.
        self.keys_down = []

    ## Handle an input-related pygame event.
    # InputManager's update function does not handle more complicated events such as "window closed."
    # Please only pass pygame mouse, keyboard, and joystick events to this function 
    def handle_event(self, event):
        if self.debug_input==True:
            if (event.type == pygame.KEYDOWN) or (event.type == pygame.KEYUP):
                print("Key pressed in InputManager: " +  pygame.key.name(event.key))

        # This next bit processes tracking which keys are currently down.
        if (event.type == pygame.KEYDOWN):
            if not (pygame.key.name(event.key) in self.keys_down):
                self.keys_down.append(pygame.key.name(event.key))
        elif (event.type == pygame.KEYUP):
            if pygame.key.name(event.key) in self.keys_down:
                self.keys_down.remove(pygame.key.name(event.key))
        self.context.handle_event(event)

    ## Change the current context to a different one, specified by name.
    def switch_context(self, name):
        if(name in self.contexts):
            self.context.detach()
            self.context = self.contexts[name]
            self.context.attach(self.keys_down)
            self.context.debug_input = self.debug_input

    def register_context(self, ctx):
        if not (ctx.name in self.contexts):
            self.contexts[ctx.name] = ctx 


