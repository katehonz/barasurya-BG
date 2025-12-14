import {
  Button,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  useDisclosure,
} from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FiEdit, FiTrash } from "react-icons/fi"

import type { AccountPublic, CustomerPublic, CustomerTypePublic, ItemCategoryPublic, ItemPublic, ItemUnitPublic, SupplierPublic, UserPublic, PurchasePublic, StorePublic, SalePublic } from "../../client"
import EditUser from "../Admin/EditUser"
import EditSupplier from "../Suppliers/EditSupplier"
import EditItemCategory from "../ItemCategories/EditItemCategory"
import EditItemUnit from "../ItemUnits/EditItemUnit"
import EditItem from "../Items/EditItem"
import EditCustomerType from "../CustomerTypes/EditCustomerType"
import EditCustomer from "../Customers/EditCustomer"
import EditAccount from "../Accounts/EditAccount"
import EditStore from "../Stores/EditStore"
import EditPurchase from "../Purchases/EditPurchase"
import EditSale from "../Sales/EditSale"
import Delete from "./DeleteAlert"

interface ActionsMenuProps {
  type: string
  value: ItemCategoryPublic | ItemPublic | UserPublic | SupplierPublic | ItemUnitPublic | CustomerTypePublic | CustomerPublic | AccountPublic | PurchasePublic | SalePublic
  disabled?: boolean
}

const ActionsMenu = ({ type, value, disabled }: ActionsMenuProps) => {
  const editUserModal = useDisclosure()
  const deleteModal = useDisclosure()
  const componentMap = {
    User: (
      <EditUser
        user={value as UserPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Item: (
      <EditItem
        item={value as ItemPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Supplier: (
      <EditSupplier
        supplier={value as SupplierPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Category: (
      <EditItemCategory
        item_category={value as ItemCategoryPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Unit: (
      <EditItemUnit
        item_unit={value as ItemUnitPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Type: (
      <EditCustomerType
        customer_type={value as CustomerTypePublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Customer: (
      <EditCustomer
        customer={value as CustomerPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Account: (
      <EditAccount
        account={value as AccountPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Store: (
      <EditStore
        store={value as StorePublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Purchase: (
      <EditPurchase
        purchase={value as PurchasePublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Sale: (
      <EditSale
        sale={value as SalePublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
  } as const;

  type ComponentKey = keyof typeof componentMap;

  function isValidComponentKey(key: string): key is ComponentKey {
    return key in componentMap;
  }


  return (
    <>
      <Menu>
        <MenuButton
          isDisabled={disabled}
          as={Button}
          rightIcon={<BsThreeDotsVertical />}
          variant="unstyled"
        />
        <MenuList>
          <MenuItem
            onClick={editUserModal.onOpen}
            icon={<FiEdit fontSize="16px" />}
          >
            Edit {type}
          </MenuItem>
          <MenuItem
            onClick={deleteModal.onOpen}
            icon={<FiTrash fontSize="16px" />}
            color="ui.danger"
          >
            Delete {type}
          </MenuItem>
        </MenuList>
        {isValidComponentKey(type) ? componentMap[type] : null}
        <Delete
          type={type}
          id={value.id}
          isOpen={deleteModal.isOpen}
          onClose={deleteModal.onClose}
        />
      </Menu>
    </>
  )
}

export default ActionsMenu
