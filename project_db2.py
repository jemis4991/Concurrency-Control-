import copy
import os
import shutil
import io
import sys

lockTableList = []
transactionTableList = []
inputOperation = []
RL = "readlock"
WL = "writeLock"
A = "Abort "
W = "Waiting"
C = "Committed"
AC = "Active"



class lockTable:
    def __init__(self, lockedDataItem, transactionID, lockState):
        self.lockedDataItem = lockedDataItem
        self.lockMode = lockState
        self.lockHeldByTransaction = []
        self.lockHeldByTransaction.append(transactionID)

    def addLockHeld(self, transactionID):
        self.lockHeldByTransaction.append(transactionID)

    def changeLockState(self, lockState):
        self.lockMode = lockState


class transactionTable():
    def __init__(self, transactionID, timeStamp, transactionState):
        self.transactionID = transactionID
        self.timeStamp = timeStamp
        self.transactionState = transactionState
        self.lockedResources = []
        self.blockedBy= []
        self.blockedOperation = []


    def changeTransactionState(self, state):
        self.transactionState = state

    def addBlockedBy(self, transactionName):
        self.blockedBy.append(transactionName)

    def addBlockedOperation(self, operation):
        self.blockedOperation.append(operation)

    def addLockedResource(self, resourceName):
        self.lockedResources.append(resourceName)




# This function is used to get the transaction number form the input operation given from the file
def get_number(operation):
    c = ""
    for i in operation:
        if i.isdigit():
            c += i
    return int(c)

#This function is used to write the simulation to the file and the output to the consol
def writeToFile():
    print("Transaction Table :")
    print("TID", end=" ")
    print("TimeStamp", end=" ")
    print("State", end=" ")
    print("LockedResources", end=" ")
    print("BlockedBy", end=" ")
    print("BlockedOperation")

    outputfile.write("\nTransaction table :\n")
    for i in range(len(transactionTableList)):
        outputfile.write("transactionID :" + str(transactionTableList[i].transactionID) + "\t")
        outputfile.write("timestamp:" + str(transactionTableList[i].timeStamp) + "\t")
        outputfile.write("transactionState:" + (transactionTableList[i].transactionState) + "\t")
        outputfile.write("Locked Resources:" + str(transactionTableList[i].lockedResources) + "\t")
        outputfile.write("Blocked By:" + str(transactionTableList[i].blockedBy) + "\t")
        outputfile.write("Blocked operations:" + str(transactionTableList[i].blockedOperation) + "\n")
        print("---------------------------------------------------------------------------------------------")
        print(transactionTableList[i].transactionID, end=' | ')
        print(transactionTableList[i].timeStamp, end=' | ')
        print(transactionTableList[i].transactionState, end=' | ')
        print(transactionTableList[i].lockedResources, end=' | ')
        print(transactionTableList[i].blockedBy, end=' | ')
        print(transactionTableList[i].blockedOperation)
    print()

    print("Lock Table:")
    print("DataItem", end=" ")
    print("LockMode", end=" ")
    print("TIDList")
    outputfile.write("\nLock table :\n")
    for i in range(len(lockTableList)):
        outputfile.write("DataItem :" + str(lockTableList[i].lockedDataItem) + "\t")
        outputfile.write("lockMode:" + str(lockTableList[i].lockMode) + "\t")
        outputfile.write("TID List:" + str(lockTableList[i].lockHeldByTransaction) + "\n")
        print("---------------------------------------------------------------------------------------------")
        print(lockTableList[i].lockedDataItem, end=' ')
        print(lockTableList[i].lockMode, end=' ')
        print(lockTableList[i].lockHeldByTransaction)
    print()


# this function is used to add the new record in the transactionTableList when a new transaction is start.
def beginOperation(operation):
    transactionNumber = get_number(operation)
    timeStamp = int(len(transactionTableList)) + 1
    transactionTableList.append(transactionTable(transactionNumber, timeStamp, AC ))


# given a input String, this function returns the resource name and the transactionID
def findResource(operation):
    resourceName= None
    if operation.find("X") != -1:
        resourceName = "X"
    elif operation.find("Y") != -1:
        resourceName = "Y"
    elif operation.find("Z") != -1:
        resourceName = "Z"
    transactionID = get_number(operation)
    return resourceName,transactionID

# this method take the transaction ID and input and searched for the transaction in the transactionTable
def searchTransaction(transactionID):
    for transaction in transactionTableList:
        if transaction.transactionID == transactionID:
            return transaction

# This function is used to put a particular resource under read lock by the transaction.
# it checks for conflicting locks and calls the wound-wait routine to prevent deadlock situations.
def readLockOperation(operation):
    resourceName = findResource(operation)[0]
    transactionID = findResource(operation)[1]
    flag = 0
    length = len(lockTableList)
    if length != 0:
        for i in range(length):
            if lockTableList[i].lockedDataItem == resourceName:
                flag = 1
                if lockTableList[
                    i].lockMode == WL:
                    # This checks if the resource requested is under a writeLock by another transaction and if thats the case, wound wait is called
                    print ("Conflicting Write lock: data item " + resourceName + " is under ReadLock by Transaction %d" % (
                        lockTableList[i].lockHeldByTransaction[0]))
                    outputfile.write("Conflicting Write lock: data item " + str(resourceName) + " is under ReadLock by Transaction " + str(
                            lockTableList[i].lockHeldByTransaction[0]))
                    print ("calling wound-wait mechanism")
                    outputfile.write("\ncalling wound-wait mechanism. ")
                    woundWait(searchTransaction(transactionID), searchTransaction(lockTableList[i].lockHeldByTransaction[0]), lockTableList[i], operation)
                elif lockTableList[
                    i].lockMode == RL:
                    # if resources is just under readLock, the new transaction is added to the list of transactions that hold a readLock on the resource
                    lockTableList[i].addLockHeld(transactionID)
                    searchTransaction(transactionID).addLockedResource(resourceName)
                    print ("Putting the data item " + resourceName + " under ReadLock by Transaction %d" % transactionID)
                    outputfile.write("Putting the data item " + str(resourceName) + " under ReadLock by Transaction " + str(transactionID))

        if flag == 0:
            lockTableList.append(lockTable(resourceName, transactionID, RL))
            # adding a new resource to the locktable if its not already in the lockTable
            searchTransaction(transactionID).addLockedResource(resourceName)
            print( "Putting the data item " + resourceName + " under ReadLock by Transaction %d" % transactionID)
            outputfile.write("Putting the data item " + str(resourceName) + " under ReadLock by Transaction " + str(transactionID))

    else:
        lockTableList.append(lockTable(resourceName, transactionID, RL))
        searchTransaction(transactionID).addLockedResource(resourceName)
        print ("Putting the data item " + resourceName + " under ReadLock by Transaction %d" % (transactionID))
        outputfile.write("Putting the data item " + str(resourceName) + " under ReadLock by Transaction " + str(transactionID))




# This function is used to put a particular resource under write lock by the transaction.
# it checks for conflicting locks and calls the wound-wait routine to prevent deadlock situations.
def writeLockOperation(operation):
    resourceName = findResource(operation)[0]
    transactionID = findResource(operation)[1]
    flag = 0
    length = len(lockTableList)
    if length != 0:
        for i in range(0, length):
            if lockTableList[i].lockedDataItem == resourceName:
                flag = 1
                if lockTableList[i].lockMode == RL:
                    if len(lockTableList[i].lockHeldByTransaction) == 1:
                        if lockTableList[i].lockHeldByTransaction[0] == transactionID:
                            # checks if the resources is under readLock by the same transaction then upgrade the write lock on that transaction.
                            lockTableList[i].changeLockState(WL)
                            print ("Upgrading Readlock to WriteLock on data item " + resourceName + " for transaction %d" % transactionID)
                            outputfile.write("Upgrading Readlock to WriteLock on data item " + resourceName + " for transaction %d. " % transactionID)

                        else:
                            print ("data item " + resourceName + "is under ReadLock by %d transaction." %(lockTableList[i].lockHeldByTransaction[0]))
                            outputfile.write("data item " + resourceName + "is under ReadLock by %d transaction. " % (lockTableList[i].lockHeldByTransaction[0]))
                            print ("call Wound Wait" )
                            outputfile.write ("\ncall Wound Wait. " )
                            # checks if the resource is under read lock by another transaction then call wound wait
                            woundWait(searchTransaction(transactionID),
                                      searchTransaction(lockTableList[i].lockHeldByTransaction[0]), lockTableList[i],
                                      operation)

                    else:

                        for lockHeld in lockTableList[i].lockHeldByTransaction:
                                if lockHeld != transactionID:
                                    print("data item " + resourceName + " is under ReadLock by %d transaction." % (lockHeld))
                                    outputfile.write("data item " + resourceName + " is under ReadLock by %d transaction. " % (lockHeld))
                                    print("call Wound Wait")
                                    outputfile.write("\ncall Wound Wait. ")
                                    # checks if requested resource is under readLock by multiple transactions then call the wund wait method iteratively for all that transaction.
                                    woundWait(searchTransaction(transactionID),
                                              searchTransaction(lockHeld), lockTableList[i],operation)


                elif lockTableList[i].lockMode == WL:
                    print ("Conflicting WriteLock: data item " + resourceName + " is under WriteLock by Transaction %d" % (
                        lockTableList[i].lockHeldByTransaction[0]))
                    outputfile.write("Conflicting WriteLock: data item " + resourceName + " is under WriteLock by Transaction %d . " % (
                            lockTableList[i].lockHeldByTransaction[0]))
                    print ("call wound wait")
                    # checks if resource is under writelock by another transaction call wound-wait
                    outputfile.write("\ncall Wound Wait. ")
                    woundWait(searchTransaction(transactionID),
                              searchTransaction(lockTableList[i].lockHeldByTransaction[0]), lockTableList[i], operation)
        if flag == 0:
            lockTableList.append(lockTable(resourceName, transactionID, WL))  # appending a new resource to the lockTable
            searchTransaction(transactionID).addLockedResource(resourceName)
            print ("data item " + resourceName + " is under WriteLock by Transaction %d" % (transactionID))
            outputfile.write("data item " + resourceName + " is under WriteLock by Transaction %d" % (transactionID))

    else:
        lockTableList.append(lockTable(resourceName, transactionID, WL))
        searchTransaction(transactionID).addLockedResource(resourceName)
        print("Putting the data item " + resourceName + " under WriteLock by Transaction %d" % (transactionID))
        outputfile.write("data item " + resourceName + " is under WriteLock by Transaction %d" % (transactionID))


# This function is called when 'e' is encounter in operation. This method commits the transaction and free all its resources also checks for waiting transaction on that transaction.
def functionEnd(operation):
    transactionNumber = get_number(operation)
    for transaction in transactionTableList:
        if transaction.transactionID == transactionNumber and transaction.transactionState != A:
            print ("Committing transaction %d" % transactionNumber)
            outputfile.write("\nCommitting transaction %d . " % transactionNumber)
            for blockedOperation in transaction.blockedOperation:
                transaction.transactionState = AC
                print("completing waiting operation " + blockedOperation)
                outputfile.write("\ncompleting waiting operation. " + blockedOperation)
                selectOperation(blockedOperation)
                unlock(transactionNumber)
            transaction.transactionState = C
            unlock(transactionNumber)
        elif transaction.transactionID == transactionNumber and transaction.transactionState == A:
            print("Transaction " + str(transactionNumber) + " is already aborted or commited. So no changes in the tables.")
            outputfile.write(
                "\nTransaction " + str(transactionNumber) + " is already aborted or commited. So no changes in the tables.\n")




# see if any transactions that were waiting for resources can now will be resumed
def startWaitingTransaction(transactionID):
    print ("checking if there are any transactions waiting on this transaction")
    outputfile.write("\nchecking if there are any transactions waiting on this transaction. ")
    for transaction in transactionTableList:
        for blockedBy in transaction.blockedBy:
            if blockedBy == transactionID:
                print("transacation is matched " + str(transaction.transactionID)+" which is blocked by transaction "+
                      str (blockedBy))
                outputfile.write("\ntransacation is matched " + str(transaction.transactionID) + " which is blocked by transaction " +
                    str(blockedBy))
                for i in range(len(transaction.blockedOperation)):
                    for blockedOperation in transaction.blockedOperation:
                        print(transaction.blockedOperation)
                        transaction.transactionState= AC
                        print("attempting operation " + blockedOperation)
                        outputfile.write("\nattempting operation " + blockedOperation)
                        transaction.blockedOperation.remove(blockedOperation)
                        selectOperation(blockedOperation)
                        # call the selectoperation method on the waiting operation and see if the transaction can now continue
                        print("blocked done")
                        print(transaction.blockedOperation)
                    if (len(transaction.blockedOperation))==0:
                        transaction.blockedBy.clear()
                        print("blocked operations are cleared ")
                        outputfile.write("\nblocked operations are cleared. ")





# unlock function releases all the resourced acquired by the transactionID passed to it
def unlock(transactionID):
    print ("Unlocking all resources held by transaction %d" % transactionID)
    outputfile.write("\nUnlocking all resources held by transaction %d. " % transactionID)
    for transaction in transactionTableList:
        if transaction.transactionID == transactionID:
            for i in range(0,len(lockTableList)):
                for resource in lockTableList:
                    for lock in transaction.lockedResources:
                        if resource.lockedDataItem == lock:
                            if len(resource.lockHeldByTransaction) == 1:
                                lockTableList.remove(resource)
                                transaction.lockedResources.remove(lock)
                                transaction.blockedBy.clear()
                                transaction.blockedOperation.clear()
                                # if only this transaction has any kind of lock on the resource,
                                # remove the resource from the lockTable completely.

                            else:
                                resource.lockHeldByTransaction.remove(transactionID)
                                transaction.lockedResources.remove(lock)
                                transaction.blockedBy.clear()
                                transaction.blockedOperation.clear()
                                # if the same sources is held by multiple transactions,
                                # remove this transaction from a that list of transactions holding the lock
    startWaitingTransaction(transactionID)

# the wound wait function deadlock prevention mechanism
def woundWait(requestingTransaction, holdingTransaction, lockedResource, operation):
    if requestingTransaction.timeStamp < holdingTransaction.timeStamp:
        holdingTransaction.changeTransactionState(A)
        print("time stamp of requestion-transaction"+str(requestingTransaction.transactionID)+
              "is less than resource holding-transaction"+str(holdingTransaction.transactionID))
        outputfile.write("\ntime stamp of requestion-transaction " + str(requestingTransaction.transactionID)
                         + " is less than resource holding-transaction " + str(holdingTransaction.transactionID))
        print ("Aborting Transaction %d" % holdingTransaction.transactionID)
        outputfile.write("\nAborting Transaction %d. " % holdingTransaction.transactionID)
        unlock(holdingTransaction.transactionID)
        # unlocking all the resources of the transaction that was aborted by wound wait
        if checkDuplicateOperation(operation, requestingTransaction):
            selectOperation(operation)

    else:
        requestingTransaction.changeTransactionState(W)
        # adds the requesting transaction to the waitingTransactions list
        print ("changing transaction state for transaction %d to blocked" % requestingTransaction.transactionID)
        outputfile.write("\nchanging transaction state for transaction %d to blocked. " % requestingTransaction.transactionID)
        if checkDuplicateOperation(operation, requestingTransaction):
            requestingTransaction.addBlockedOperation(operation)
        searchTransaction(requestingTransaction.transactionID).addBlockedBy(holdingTransaction.transactionID)


def checkDuplicateOperation(operation, transaction):
    for blockedOperation in transaction.blockedOperation:
        if blockedOperation == operation:
            return 0
    return 1

# this function checks the state of the transaction that if the transaction is aborted, the operation will be ignored
def checkState(operation):
    # resourceName = findResource(operation)[0]
    transactionID = findResource(operation)[1]

    length = len(transactionTableList)
    if length != 0:
        for i in range(0, length):
            if transactionTableList[i].transactionID == transactionID and transactionTableList[i].transactionState == W:
                outputfile.write("transaction state of tranaction "+ str(transactionTableList[i].transactionID) +" waiting.\nso "
                                 + str(operation)+ "is added to blocked operation.")
                print("transaction state of tranaction " + str(transactionTableList[i].transactionID) + " waiting.so "
                     + str(operation) + "is added to blocked operation.")
                transactionTableList[i].addBlockedOperation(operation)
                operation = ""
                writeToFile()
            elif transactionTableList[i].transactionID == transactionID and (transactionTableList[i].transactionState == A or transactionTableList[i].transactionState == C):
                operation = ""
                print("Operation Ignored. Transaction " + str(transactionID)+" is already aborted or commited. So no changes in the tables. ")
                outputfile.write("\nTransaction " + str(transactionID)+" is already aborted or commited. So no changes in the tables.\n")

    return operation


# this method used to processes the operation form input file and calls the function accordingly.
def selectOperation(operation):
    outputfile.write("\n\n\nperforming operation " + str(operation))
    print("performing operation " + str(operation))
    if operation.find('e') == -1:
        operation = checkState(operation)
    if operation.find('b') != -1:
        print("\nTransaction begin :")
        beginOperation(operation)
        writeToFile()
    elif operation.find('r') != -1:
        print ("\nRead operation :")
        readLockOperation(operation)
        writeToFile()
    elif operation.find('w') != -1:
        print ("\nwrite operation :")
        writeLockOperation(operation)
        writeToFile()
    elif operation.find("e") != -1:
        print ("\nend operation")
        functionEnd(operation)
        writeToFile()


file=input("enter the input file name")
outfile=input("Enter the output file name")
if file=="x":
    sys.exit()
else:
    if file.endswith('.txt'):
        print('\n' + file.split('.txt')[0] + '\n')
    outputfile= open(outfile, "w+" )
    with open(file, 'r') as text:
        for line in text:
            inputOperation.append(line)
    print(inputOperation)
    for operation in inputOperation:
        selectOperation(operation)
    outputfile.close()

#references
#github.com
#geeksforgeeks.org
#tutorialspoint.com