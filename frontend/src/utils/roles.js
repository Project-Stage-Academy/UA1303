export const ROLE_MAP = {
    startup: 1,
    investor: 2,
  };
  
  export const getRoleId = (roleName) => ROLE_MAP[roleName] || null;
  
  export const getRoleName = (roleId) => {
    return Object.keys(ROLE_MAP).find((key) => ROLE_MAP[key] === roleId) || null;
  };