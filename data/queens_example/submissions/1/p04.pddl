(define (problem p4-dungeon)
  (:domain Dungeon)

  ; Come up with your own problem instance (see assignment for details)
  ; NOTE: You _may_ use new objects for this problem only.

  ; Naming convention:
  ; - loc-{i}-{j} refers to the location at the i'th column and j'th row (starting in top left corner)
  ; - c{i}{j}{h}{k} refers to the corridor connecting loc-{i}-{j} and loc-{h}-{k}
  (:objects
    loc-2-1 loc-3-1 loc-1-2 loc-2-2 loc-3-2 loc-1-3 loc-2-3 loc-3-3 - location
    c1213 c1222 c1221 c2131 c2132 c2122 c2232 c3132 c3233 c3323 - corridor
    key1 key2 key3 key4 key5 - key
  )

  (:init
    ; -- Problem setting diagram in group-contributions.pdf

    ; Hero location and carrying status
    (hero-at loc-1-2)
    (arm-free)

    ; Location <> Corridor Connections
    (corridor-between loc-1-2 loc-1-3 c1213)
    (corridor-between loc-1-3 loc-1-2 c1213)
    (connected loc-1-2 c1213)
    (connected loc-1-3 c1213)

    (corridor-between loc-1-2 loc-2-2 c1222)
    (corridor-between loc-2-2 loc-1-2 c1222)
    (connected loc-1-2 c1222)
    (connected loc-2-2 c1222)

    (corridor-between loc-1-2 loc-2-1 c1221)
    (corridor-between loc-2-1 loc-1-2 c1221)
    (connected loc-1-2 c1221)
    (connected loc-2-1 c1221)

    (corridor-between loc-2-1 loc-3-1 c2131)
    (corridor-between loc-3-1 loc-2-1 c2131)
    (connected loc-2-1 c2131)
    (connected loc-3-1 c2131)

    (corridor-between loc-2-1 loc-3-2 c2132)
    (corridor-between loc-3-2 loc-2-1 c2132)
    (connected loc-2-1 c2132)
    (connected loc-3-2 c2132)

    (corridor-between loc-2-1 loc-2-2 c2122)
    (corridor-between loc-2-2 loc-2-1 c2122)
    (connected loc-2-1 c2122)
    (connected loc-2-2 c2122)

    (corridor-between loc-2-2 loc-3-2 c2232)
    (corridor-between loc-3-2 loc-2-2 c2232)
    (connected loc-2-2 c2232)
    (connected loc-3-2 c2232)

    (corridor-between loc-3-1 loc-3-2 c3132)
    (corridor-between loc-3-2 loc-3-1 c3132)
    (connected loc-3-1 c3132)
    (connected loc-3-2 c3132)

    (corridor-between loc-3-2 loc-3-3 c3233)
    (corridor-between loc-3-3 loc-3-2 c3233)
    (connected loc-3-2 c3233)
    (connected loc-3-3 c3233)

    (corridor-between loc-3-3 loc-2-3 c3323)
    (corridor-between loc-2-3 loc-3-3 c3323)
    (connected loc-3-3 c3323)
    (connected loc-2-3 c3323)

    ; Key locations
    (key-at key1 loc-1-2)
    (key-at key2 loc-1-2)
    (key-at key3 loc-2-1)
    (key-at key4 loc-1-3)
    (key-at key5 loc-1-3)

    ; Locked corridors
    (locked c1213)
    (locked c1222)
    (locked c1221)
    (locked c2131)
    (locked c2132)
    (locked c2122)
    (locked c2232)
    (locked c3233)
    (locked c3323)

    ; Lock colours
    (lock-colour c1213 yellow)
    (lock-colour c1222 purple)
    (lock-colour c1221 red)
    (lock-colour c2131 red)
    (lock-colour c2132 red)
    (lock-colour c2122 yellow)
    (lock-colour c2232 red)
    (lock-colour c3233 green)
    (lock-colour c3323 rainbow)

    ; Risky corridors
    (risky c1221)
    (risky c2131)
    (risky c2132)
    (risky c2232)

    ; Key colours
    (key-colour key1 red)
    (key-colour key2 yellow)
    (key-colour key3 purple)
    (key-colour key4 green)
    (key-colour key5 rainbow)

    ; Key usage properties (one use, two use, etc)
    (key-usable key1)
    (key-usable key2)
    (key-usable key3)
    (key-usable key4)
    (key-usable key5)

    (key-double-use key2)
    (key-single-use key3)
    (key-single-use key4)
    (key-single-use key5)

  )
  (:goal
    (and
      ; Hero's final location goes here
      (hero-at loc-2-3)
    )
  )

)