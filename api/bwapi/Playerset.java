package bwapi;

import bwapi.*;

import java.util.Map;
import java.util.HashMap;
import java.util.Collection;
import java.util.List;

public class Playerset {

    public List<Unit> getUnits() {
        return getUnits_native(pointer);
    }

    public void setAlliance(boolean allies) {
        setAlliance_native(pointer, allies);
    }

    public void setAlliance() {
        setAlliance_native(pointer);
    }

    public void setAlliance(boolean allies, boolean alliedVictory) {
        setAlliance_native(pointer, allies, alliedVictory);
    }


    private static Map<Long, Playerset> instances = new HashMap<Long, Playerset>();

    private Playerset(long pointer) {
        this.pointer = pointer;
    }

    private static Playerset get(long pointer) {
        if (pointer == 0 ) {
            return null;
        }
        Playerset instance = instances.get(pointer);
        if (instance == null ) {
            instance = new Playerset(pointer);
            instances.put(pointer, instance);
        }
        return instance;
    }

    private long pointer;

    private native List<Unit> getUnits_native(long pointer);

    private native void setAlliance_native(long pointer, boolean allies);

    private native void setAlliance_native(long pointer);

    private native void setAlliance_native(long pointer, boolean allies, boolean alliedVictory);


}
