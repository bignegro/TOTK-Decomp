ENTRY(entry)

SECTIONS
{
  . = 0x7100000000;

  .text : ALIGN(16)
  {
    *(.text.entry)
    *(.text*)
  }

  .rodata : ALIGN(16)
  {
    *(.rodata*)
  }

  .data : ALIGN(16)
  {
    *(.data*)
  }

  .bss (NOLOAD) : ALIGN(16)
  {
    *(.bss*)
    *(COMMON)
  }
}
