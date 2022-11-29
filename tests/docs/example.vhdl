library ieee;
use     ieee.std_logic_1164.all;
use     ieee.numeric_std.all;

--
entity entity_1 is
	generic (
		FREQ : real     := (100.0 * 1024.0 * 1024.0);   -- Frequency in Hz
		BITS : positive := 8                            -- Number of counter bits
	);
	port (
	  Clock: in  std_logic;                           -- module clock
	  Reset: in  std_logic := '0';                    -- module reset
	  Q:     out std_logic_vector(BITS - 1 downto 0)  -- Counter value
	);
end entity entity_1;

architecture rtl of entity_1 is
	signal Reset_n : std_logic;
begin
	Reset_n <= (not Reset);

	process(Clock)
	begin
		if rising_edge(Clock) then
			if Reset_n = '0' then
				Q <= (others => '0');
			else
				Q <= std_logic_vector(unsigned(Q) + 1);
			end if;
		end if;
	end process;
end architecture rtl;
