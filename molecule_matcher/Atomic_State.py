from threading import Thread, Lock

from pyflexy.util.Log import Log
from Atom import Atom
from Atom_Set import Atom_Set
from Bond import Bond
from Bond_Set import Bond_Set

class Atomic_State( Thread ):
    """models the state of a set of atoms by reading flexy events from queue
    """

    LOG = Log( name="l33tgui.Molecule_Matcher.Atomic_State", level=Log.DEBUG )
    NULL_BOND = (0, 0)

    def __init__( self, event_queue, atom_dictionary ):
        # queue to read events from
        self.event_queue = event_queue

        # dictionary associating hub addresses with types of atoms
        self.atom_dictionary = atom_dictionary

        # lock to assure that state isn't read while it is being adjusted
        self.lock = Lock()

        # hook to recieve notification of changes to data structure
        self.on_change = None
        
        # data structures modeling current state of atoms
        self.atoms = {} # atoms by address
        self.free_atom_set = Atom_Set()
        self.bonds = {} # bonds by address
        self.bonds_set = Bond_Set()
        self.possible_molecules = []

    def run( self ):
        # read events from queue while it exists
        while( self.event_queue ):
            try:
                event = self.event_queue.get( timeout=1 )

                # acquire state lock to assure state changes are atomic
                self.lock.acquire()

                # take appropriate action for event
                try:
                    if event["type"] == "create":
                        self._create_atom( address=event["hub"] )
                    elif event["type"] == "destroy":
                        self._destroy_atom( address=event["hub"] )
                    elif event["type"] == "connect":
                        self._bond_atom( atom_address=event["hub"],
                                         number=event["socket"],
                                         bond_address=event["strut"] )
                    elif event["type"] == "disconnect":
                        self._unbond_atom( address=event["hub"],
                                           number=event["socket"] )
                    elif event["type"] == "configure":
                        self._configure_bond( address=event["hub"],
                                              number=event["socket"],
                                              pitch=event["pitch"],
                                              roll=event["roll"],
                                              yaw=event["yaw"] )
                    else raise KeyError # unrecognized event type

                except KeyError:
                    self.LOG.warn( "malformed flexy event: %s" % event )

                # release state lock
                self.lock.release()

                # call on change handler
                if self.on_change is not None:
                    self.on_change()
                
            except Empty:
                self.LOG.debug( "event_queue.get(): timeout" )
                

    def _create_atom( self, address ):
        """create a new atom with the given address
        """
        # look up attributes for new atom in dictionary
        atom = Atom( address=address,
                     symbol=self.atom_dictionary[address]["symbol"],
                     name=self.atom_dictionary[address]["name"],
                     bonds=self.atom_dictionary[address]["bonds"] )

        # add to atoms dict and free atoms set
        self.atoms[atom.address] = atom
        self.free_atom_set.add( atom )

    def _destroy_atom( self, address ):
        """remove atom with the given address from the current state
        """
        try:
            self.free_atom_set.remove( atom )
            del self.atoms[atom.address]
        except KeyError:
            raise KeyError( "destroyed atom not in free atom set: %s!"
                            % atom )
        
    def _bond_atom( self, atom_address, number, bond_address ):
        """connect atom with the given address to bond with the given address
           at given bond number of atom
        """
        # if bond with given address doesn't already exist create it
        if not self.bonds.has_key( bond_address ):
            self.bonds[bond_address] = Bond( address=bond_address )
        bond = self.bonds[bond_address]

        # get atom
        atom = self.atoms[atom_address]

        # vet number
        if atom.bonds[number] is not None:
            raise ValueError( "atom bond slot already occupied" )

        # if atom is in free atom set remove it and create a new possible
        # molecule
        if atom in self.free_atom_set:
            self.free_atom_set.remove( atom )
            possible = Possible_Molecule()
            possible.atom_set.add( atom )
            self.possible_molecules.append( possible )

        # add atom to bond, bond to atom and bond to bond set
        atom.bonds[number] = bond
        bond.atom_set.add( atom )
        self.bond_set.add( atom, bond )
        
            
        

    def _configure_bond( self, address, number, pitch, roll, yaw ):
        """configure the angle of a bond to the atom it is bonded to
        """
