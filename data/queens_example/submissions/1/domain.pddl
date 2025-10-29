(define (domain Dungeon)

    (:requirements :typing :negative-preconditions :conditional-effects :equality
    )

    ; Do not modify the types
    (:types
        location colour key corridor
    )

    ; Do not modify the constants
    (:constants
        red yellow green purple rainbow - colour
    )

    ; You may introduce whatever predicates you would like to use
    (:predicates

        ; One predicate given for free!
        (hero-at ?loc - location)

        ; WORLD
        (connected ?loc - location ?cor - corridor) ; Room is connected to corridor
        (corridor-between ?from ?to - location ?cor - corridor) ; Corridor exists between two locations
        (locked ?cor - corridor) ; Corridor is locked
        (lock-colour ?cor - corridor ?col - colour) ; Corridor lock colour
        (messy ?loc - location) ; Location is messy
        (collapsed ?cor - corridor) ; Corridor is collapsed
        (risky ?cor - corridor) ; Corridor is risky

        ; KEY
        (key-at ?k - key ?loc - location) ; Key is at location
        (key-usable ?k - key) ; Key is usable (has uses left)
        (key-single-use ?k - key) ; Key has one use left
        (key-double-use ?k - key) ; Key has two uses left
        (key-colour ?k - key ?col - colour) ; Key colour

        ; HERO
        (holding ?k - key) ; Hero is holding key
        (arm-free) ; Hero's arm is free (not holding a key)

    )

    ; IMPORTANT: You should not change/add/remove the action names or parameters

    ;Hero can move if the
    ;    - hero is at current location ?from,
    ;    - hero will move to location ?to,
    ;    - corridor ?cor exists between the ?from and ?to locations
    ;    - there isn't a locked door in corridor ?cor
    ;Effects move the hero, and collapse the corridor if it's "risky" (also causing a mess in the ?to location)
    (:action move

        :parameters (?from ?to - location ?cor - corridor)

        :precondition (and

            ; Allow moving only if:
            (hero-at ?from) ; Hero is at the current location
            (corridor-between ?from ?to ?cor) ; Corridor exists between the current and target locations
            (not (locked ?cor)) ; Corridor is not locked
            (not (collapsed ?cor)) ; Corridor has not collapsed

        )

        :effect (and

            ; Set hero to new location and no longer at old location:
            (hero-at ?to)
            (not (hero-at ?from))

            ; Set corridor collapsed and location messy if corridor is risky:
            (when
                (risky ?cor)
                (and
                    (messy ?to)
                    (collapsed ?cor)
                )
            )

        )
    )

    ;Hero can pick up a key if the
    ;    - hero is at current location ?loc,
    ;    - there is a key ?k at location ?loc,
    ;    - the hero's arm is free,
    ;    - the location is not messy
    ;Effect will have the hero holding the key and their arm no longer being free
    (:action pick-up

        :parameters (?loc - location ?k - key)

        :precondition (and

            ; Allow picking up only if:
            (hero-at ?loc) ; Hero is at the location
            (key-at ?k ?loc) ; Key is at the location
            (arm-free) ; Hero's arm is free
            (not (messy ?loc)) ; Location is not messy

        )

        :effect (and

            ; Set hero holding key, arm not free and key not at location:
            (holding ?k)
            (not (arm-free))
            (not (key-at ?k ?loc))

        )
    )

    ;Hero can drop a key if the
    ;    - hero is holding a key ?k,
    ;    - the hero is at location ?loc
    ;Effect will be that the hero is no longer holding the key
    (:action drop

        :parameters (?loc - location ?k - key)

        :precondition (and

            ; Allow dropping only if the hero is holding the key and the hero is at the location attempting to drop at:
            (not (arm-free))
            (holding ?k)
            (hero-at ?loc)

        )

        :effect (and

            ; Set hero arm free, key not held and key at location:
            (arm-free)
            (not (holding ?k))
            (key-at ?k ?loc)

        )
    )

    ;Hero can use a key for a corridor if
    ;    - the hero is holding a key ?k,
    ;    - the key still has some uses left,
    ;    - the corridor ?cor is locked with colour ?col,
    ;    - the key ?k is if the right colour ?col,
    ;    - the hero is at location ?loc
    ;    - the corridor is connected to the location ?loc
    ;Effect will be that the corridor is unlocked and the key usage will be updated if necessary
    (:action unlock

        :parameters (?loc - location ?cor - corridor ?col - colour ?k - key)

        :precondition (and

            ; Allow unlocking only if:
            (holding ?k) ; Hero is holding the key
            (key-usable ?k) ; Key is usable
            (locked ?cor) ; Corridor is locked
            (lock-colour ?cor ?col) ; Corridor is locked with the right colour
            (key-colour ?k ?col) ; Key is of the right colour
            (hero-at ?loc) ; Hero is at the location
            (connected ?loc ?cor) ; Corridor is connected to the location
        )

        :effect (and

            ; Set corridor not locked:

            ; When key is single use, set key not usable:
            (not (locked ?cor))
            (when
                (key-single-use ?k)
                (and
                    (not (key-single-use ?k))
                    (not (key-usable ?k))
                )
            )

            ; When key is double use, set key single use:
            (when
                (key-double-use ?k)
                (and
                    (not (key-double-use ?k))
                    (key-single-use ?k)
                )
            )
        )
    )

    ;Hero can clean a location if
    ;    - the hero is at location ?loc,
    ;    - the location is messy
    ;Effect will be that the location is no longer messy
    (:action clean

        :parameters (?loc - location)

        :precondition (and

            ; Allow cleaning only if the hero is at the location and the location is messy:
            (hero-at ?loc)
            (messy ?loc)

        )

        :effect (and

            ; Set room not messy:
            (not (messy ?loc))

        )
    )

)