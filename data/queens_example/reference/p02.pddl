(define (problem p2-dungeon)
  (:domain Dungeon)
  (:objects
    loc-2-1 loc-1-2 loc-2-2 loc-3-2 loc-4-2 loc-2-3 - location
    key1 key2 key3 key4 - key
    c2122 c1222 c2232 c3242 c2223 - corridor
  )

  (:init

    (hero-at loc-2-2)

    (connected loc-2-1 c2122)
    (connected loc-2-2 c2122)
    (connected loc-1-2 c1222)
    (connected loc-2-2 c1222)
    (connected loc-2-2 c2232)
    (connected loc-3-2 c2232)
    (connected loc-3-2 c3242)
    (connected loc-4-2 c3242)
    (connected loc-2-2 c2223)
    (connected loc-2-3 c2223)

    (in key1 loc-2-1)
    (in key2 loc-1-2)
    (in key3 loc-2-2)
    (in key4 loc-2-3)

    (locked c2122 purple)
    (locked c1222 yellow)
    (locked c2232 yellow)
    (locked c3242 rainbow)
    (locked c2223 green)

    (arm-free)

    (key-colour key1 green)
    (key-colour key2 rainbow)
    (key-colour key3 purple)
    (key-colour key4 yellow)

    (two-use key4)
    (one-use key3)
    (one-use key1)
  )
  (:goal
    (and (hero-at loc-4-2))
  )

)
