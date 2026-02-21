add_subdirectory(Game)
add_subdirectory(KingSystem)

target_sources(totk PRIVATE
  entry.S
  stubs.c
)
