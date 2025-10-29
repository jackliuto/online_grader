(define (domain Dungeon)

    (:requirements
        :typing
        :negative-preconditions
        :conditional-effects
        :equality
    )

    (:types
        location colour key corridor
    )

    (:constants
        red yellow green purple rainbow - colour
    )

    (:predicates

        (hero-at ?loc - location)
        (in ?k - key ?loc - location)

        (connected ?loc - location ?cor - corridor)
        (risky ?cor - corridor)
        (locked ?cor - corridor ?col - colour)

        (arm-free)
        (holding ?k - key)

        (key-colour ?k - key ?col - colour)
        (two-use ?k - key)
        (one-use ?k - key)
        (no-use ?k - key)

        (messy ?loc - location)

    )

    ;Hero can move if the
    ;    - hero is at current location ?from,
    ;    - wants to move to location ?to,
    ;    - corridor ?cor exists between the ?from and ?to locations
    ;    - there isn't a locked door in corridor ?cor
    ;Effects move the hero, and collapse the corridor + make destination "messy" if it's "risky"
    (:action move
        :parameters (?from ?to - location ?cor - corridor)
        :precondition (and
                            (connected ?from ?cor)
                            (connected ?to ?cor)
                            (hero-at ?from)
                            (not (= ?from ?to))

                            (forall (?col - colour) (not (locked ?cor ?col)))

        )
        :effect (and
                            (hero-at ?to)
                            (not (hero-at ?from))

                            (when (risky ?cor)
                                (and (messy ?to)
                                     (not (connected ?from ?cor))
                                     (not (connected ?to ?cor))))
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
            (hero-at ?loc)
            (in ?k ?loc)
            (arm-free)
            (not (messy ?loc))
        )
        :effect (and
            (holding ?k)
            (not (in ?k ?loc))
            (not (arm-free))
        )
    )

    ;Hero can drop a key if the
    ;    - hero is holding a key ?k,
    ;    - the hero is at location ?loc
    ;Effect will be that the hero is no longer holding the key
    (:action drop
        :parameters (?loc - location ?k - key)
        :precondition (and
            (holding ?k)
            (hero-at ?loc)
        )
        :effect (and
            (not (holding ?k))
            (in ?k ?loc)
            (arm-free)
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
            (locked ?cor ?col)
            (holding ?k)
            (key-colour ?k ?col)
            (hero-at ?loc)
            (connected ?loc ?cor)
            (not (no-use ?k))
        )
        :effect (and
            (not (locked ?cor ?col))
            (when (two-use ?k) (and (not (two-use ?k)) (one-use ?k)))
            (when (one-use ?k) (and (not (one-use ?k)) (no-use ?k)))
        )
    )

    ;Hero can clean a location if
    ;    - the hero is at location ?loc,
    ;    - the location is messy
    ;Effect will be that the location is no longer messy
    (:action clean
        :parameters (?loc - location)
        :precondition (and (hero-at ?loc) (messy ?loc))
        :effect (and (not (messy ?loc)))
    )




)
