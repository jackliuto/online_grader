(define (problem p2-dungeon)
  (:domain Dungeon)

  ; Naming convention:
  ; - loc-{i}-{j} refers to the location at the i'th column and j'th row (starting in top left corner)
  ; - c{i}{j}{h}{k} refers to the corridor connecting loc-{i}-{j} and loc-{h}-{k}
  (:objects
    loc-2-1 loc-1-2 loc-2-2 loc-3-2 loc-4-2 loc-2-3 - location
    key1 key2 key3 key4 - key
    c2122 c1222 c2232 c3242 c2223 - corridor
  )

  (:init

    ; Hero location and carrying status
    (hero-at loc-2-2)
    (arm-free)

    ; Location <> Corridor Connections
    (corridor-between loc-2-1 loc-2-2 c2122)
    (corridor-between loc-2-2 loc-2-1 c2122)
    (connected loc-1-2 c2122)
    (connected loc-2-2 c2122)

    (corridor-between loc-1-2 loc-2-2 c1222)
    (corridor-between loc-2-2 loc-1-2 c1222)
    (connected loc-1-2 c1222)
    (connected loc-2-2 c1222)

    (corridor-between loc-2-2 loc-3-2 c2232)
    (corridor-between loc-3-2 loc-2-2 c2232)
    (connected loc-2-2 c2232)
    (connected loc-3-2 c2232)

    (corridor-between loc-3-2 loc-4-2 c3242)
    (corridor-between loc-4-2 loc-3-2 c3242)
    (connected loc-3-2 c3242)
    (connected loc-4-2 c3242)

    (corridor-between loc-2-2 loc-2-3 c2223)
    (corridor-between loc-2-3 loc-2-2 c2223)
    (connected loc-2-2 c2223)
    (connected loc-2-3 c2223)

    ; Key locations
    (key-at key1 loc-2-1)
    (key-at key2 loc-1-2)
    (key-at key3 loc-2-2)
    (key-at key4 loc-2-3)

    ; Locked corridors
    (locked c2122)
    (locked c1222)
    (locked c2223)
    (locked c2232)
    (locked c3242)

    ; Lock colours
    (lock-colour c2122 purple)
    (lock-colour c1222 yellow)
    (lock-colour c2223 green)
    (lock-colour c2232 yellow)
    (lock-colour c3242 rainbow)

    ; Risky corridors
    ; none

    ; Key colours
    (key-colour key1 green)
    (key-colour key2 rainbow)
    (key-colour key3 purple)
    (key-colour key4 yellow)

    ; Key usage properties (one use, two use, etc)
    (key-usable key1)
    (key-usable key2)
    (key-usable key3)
    (key-usable key4)

    (key-single-use key1)
    (key-single-use key2)
    (key-single-use key3)
    (key-double-use key4)

  )
  (:goal
    (and
      ; Hero's final location goes here
      (hero-at loc-4-2)
    )
  )

)