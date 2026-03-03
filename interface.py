from typing import List
from langchain_core.messages import BaseMessage, HumanMessage

def display_agent_output(agent_name: str, message: str):
    """Formats and prints agent output to the console."""
    print(f"\n" + "="*50)
    print(f"AGENT: {agent_name}")
    print("-" * 50)
    print(message)
    print("=" * 50 + "\n")

def get_human_input(context: str) -> str:
    """Prompts the user for input with context."""
    print("\n" + "?"*50)
    print("HUMAN INTERVENTION REQUIRED")
    print(f"Context: {context}")
    print("-" * 50)
    feedback = input("Your comment, question, or guidance: ")
    print("?" * 50 + "\n")
    return feedback

NIDUS_ASCII_ART = """                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                  ::::                                              
                                                    ::::::::                                        
                                           :--:::::::      ::::                                     
                                      :------::    :::::---   ::--                                  
                                   ----::------::----    :--:    --                                 
                                 :--:-------  :--: ::----   -:-   ---                               
                               :------   -==-----       :---  ---   --                              
                              ---=-   ===-                ::-- ---   --                             
                             --==   -==        :--::        :--  --   --                            
                            ===-   ==        -----:::::       --  --   --                           
                           --=   -=-     -------::::::::::     -- :-   :-                           
                          :==:   =-     ===----:::::::::-===    -- --   -:                          
                          -=-   =-     :=====+********++++++    :- --   --                          
                          ==   -= -    :=====+++++++++++++++     - --   -+                          
                          ==   ==-+    :====++++++++++++++++     - =-   =+                          
                          ==   +::+    :++++++++++++++++++++       =    ==                          
                          ==   +: +    :++****++++++++*#*+++      ==   -==                          
                          -=   == ++    **************#####*     ==   -=+                           
                           =   :+  +=   -+***********####*+     ==   -===                           
                           ==   += =+=     =+*******##*+       ==   =+==                            
                            +-   += =+=       =+****+-       ===   ====                             
                            -+-  :++  ++=                 -===   ===+=                              
                             -+=   ++: +++=:         --====-  :=====-                               
                               ++:  =++-  ++==--  ====--  ---==-===                                 
                                ===   =++=-  -==-==========---==-                                   
                                  ===-   =====--     =--=====-                                      
                                    -===-:    ==+++=====-:                                          
                                       :-=======::                                                  
                                             -====                                                  
                                                                                                    
                                                                                                    
                             ##        #             ##                                             
                             ###       #  ##         ##                                             
                             # ###     #             ##                                             
                             #  ###    #  %#  ######### #      #  ####                              
                             #    ###  #  %# ##     ### #      #  ###                               
                             #     ### #  %# ##      ## #      #    ###                             
                             #       ###  %# ##     ### ##     #      #                             
                             #        ##  %#  #########  ####### %#####                             
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    
                                                                                                    """

def print_welcome(framework_name: str, description: str):
    """Prints a welcome message."""
    print(NIDUS_ASCII_ART)
    print("\n" + "#" * 60)
    print(f"# {framework_name.upper()}")
    print(f"# {description}")
    print("#" * 60 + "\n")
