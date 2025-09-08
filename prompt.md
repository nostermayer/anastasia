### **Task: Python Class Generation**

Generate a complete, runnable Python script that defines a mixin class named Anastasia for adding "temporal" functionality to objects. The final output must be a single, self-contained Python file.

### **Core Functionality**

The goal is to create a "time-travel" feature that allows an object's state to be viewed as it was at a specific point in time. This is managed by a class-level as\_of\_timestamp.

### **Class Details**

1. **Anastasia Class (Mixin):**  
   * **Class Variable:** It must have a class variable as\_of\_timestamp which defaults to None.  
   * **Context Manager:** Implement a class-level context manager named context. It takes an optional timestamp (a datetime.datetime object). When a user enters a with block, it sets Anastasia.as\_of\_timestamp to the provided value. It must reliably reset the timestamp to its original value upon exiting the block, even if an exception occurs.  
   * **Decorator:** Implement a static method decorator temporal\_attribute. This decorator will be used to mark which attributes on a class should be snapshotted. It should accept an initial value from the decorated method.  
2. **TemporalAttribute Class (Descriptor):**  
   * This class is a Python descriptor. It is returned by the Anastasia.temporal\_attribute decorator.  
   * It must handle the \_\_get\_\_ and \_\_set\_\_ logic for the decorated attribute.  
   * **Snapshot Storage:** It must maintain a private dictionary \_snapshots to store historical values. The keys of this dictionary should be datetime.datetime objects (the snapshot timestamp) and the values should be a **deep copy** of the attribute's state.  
   * **\_\_get\_\_ Method:**  
     * If Anastasia.as\_of\_timestamp is None, it should return the attribute's current, live value.  
     * If Anastasia.as\_of\_timestamp is set, it must find the most recent snapshot that was taken **at or before** the specified timestamp.  
     * If no such snapshot exists, it must raise a ValueError.  
     * It should lazily load and take an initial snapshot using the decorated method's return value the first time the attribute is accessed.  
   * **\_\_set\_\_ Method:**  
     * This method should handle normal attribute assignment (e.g., company.credit\_rating \= "B"). It should update the live value but **not** automatically create a new snapshot.  
   * **set\_snapshot() Method:**  
     * This method must be callable by the user to explicitly take a new snapshot of the attribute's current value. For example: company.credit\_rating.set\_snapshot("B").

### **Implementation Guidelines**

* Use only standard Python libraries (datetime, copy, contextlib, sys).  
* Include comprehensive docstrings and inline comments.  
* The script must be self-contained and include a if \_\_name\_\_ \== '\_\_main\_\_': block with a clear, runnable example demonstrating all features. The example should show how to set the attribute with a default value, how to take new snapshots, and how to use the context manager to view the object's historical state.