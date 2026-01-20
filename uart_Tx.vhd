library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity uart_rx is
    Port (
        clk         : in  STD_LOGIC;
        rx          : in  STD_LOGIC;
        dato_rx     : out STD_LOGIC_VECTOR(7 downto 0);
        dato_valido : out STD_LOGIC
    );
end uart_rx;

architecture Behavioral of uart_rx is
    -- 100MHz / 9600 = 10416
    constant CICLOS_POR_BIT : integer := 41666;
    type t_estado is (IDLE, START, DATOS, STOP);
    signal estado : t_estado := IDLE;
    
    signal contador : integer range 0 to CICLOS_POR_BIT := 0;
    signal bit_idx  : integer range 0 to 7 := 0;
    signal reg_dato : std_logic_vector(7 downto 0) := (others => '0');
    
begin
    process(clk)
    begin
        if rising_edge(clk) then
            dato_valido <= '0'; -- por defecto
            
            case estado is
                -- esperamos bit de inicio
                when IDLE =>
                    contador <= 0; --reiniciamos el contador
                    bit_idx  <= 0; --reinicionamos el indice del bit
                    if rx = '0' then -- detecta bajada
                        estado <= START;--pasamos al siguiente estado
                    end if;

                -- esperamos medio bit
                when START =>
                    if contador = (CICLOS_POR_BIT / 2) then
                        if rx = '0' then -- verificamos el bit
                            contador <= 0; --reiniciamos el contador
                            estado   <= DATOS; --pasamos al siguiente estadi
                        else
                            estado   <= IDLE; -- volvemos al estado anteior
                        end if;
                                                           
                    else
                        contador <= contador + 1;
                    end if;

                -- leemos los 8 bits
                when DATOS =>
                    -- se muestrea en la mitad del bit
                    if contador = (CICLOS_POR_BIT / 2) then
                        reg_dato(bit_idx) <= rx; -- agregamos el bit al registro
                    end if;
                
                    if contador = (CICLOS_POR_BIT - 1) then
                        contador <= 0; --reiniciamos el contador
                        if bit_idx = 7 then -- cuando se registraron los 8 bits pasamos al siguiente estado
                            estado <= STOP;
                        else
                            bit_idx <= bit_idx + 1; --actualiamos el numero de bit
                        end if;
                    else
                        contador <= contador + 1; --actualiazanis el contador
                    end if;

                -- 4. Terminamos y avisamos
                when STOP =>
                    if contador = (CICLOS_POR_BIT - 1) then
                        contador <= 0; -- reinciamos el contador
                        dato_valido <= '1'; --bit enviado correctamente
                        dato_rx <= reg_dato; -- actualizamos la slaida del bit
                        estado <= IDLE; --volvemos al etado de reposo
                    else
                        contador <= contador + 1; --actualizamos el contador
                    end if;

            end case;
        end if;
    end process;
end Behavioral;
