<%@ page contentType="text/html" %>
<%@ taglib prefix="c"      uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt"    uri="http://java.sun.com/jsp/jstl/fmt" %>
<html><head><title>Pet Store Demo</title>
<meta content="text/html; charset=windows-1252" http-equiv="Content-Type" />
<META HTTP-EQUIV="Cache-Control" CONTENT="max-age=0">
<META HTTP-EQUIV="Cache-Control" CONTENT="no-cache">
<meta http-equiv="expires" content="0">
<META HTTP-EQUIV="Expires" CONTENT="Tue, 01 Jan 1980 1:00:00 GMT">
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
</head>

<body bgcolor="white">

  <script type="text/javascript">
    let utag_data = {"adl_site_hierarchy":["magazine"],"adl_category":"petstore","adl_subcategory":"","adl_language":"en","adl_country":"language-masters","adl_page_type":"","page_name":"petstore","adl_page_url":"http://jpetstore-web.cd6578cfa15a4488b1b8.eastus.aksapp.io/shop/index.do"};
  </script>

  <script type="text/javascript">
    function importUtagScript() {
        (function(a,b,c,d){
            a='https://tags.tiqcdn.com/utag/kyndryl/dev/dev/utag.js';
            b=document;c='script';d=b.createElement(c);d.src=a;d.type='text/java'+c;d.async= true;
            a=b.getElementsByTagName(c)[3];a.parentNode.insertBefore(d,a);
        })();
    }
  </script>

<table background="../images/bkg-topbar.gif" border="0" cellspacing="0" cellpadding="5" width="100%">
  <tbody>
  <tr>
    <td><a href="<c:url value="/shop/index.do"/>"><img border="0" src="../images/logo-topbar.gif" /></a></td>
    <td align="right"><a href="<c:url value="/shop/viewCart.do"/>"><img border="0" name="img_cart" src="../images/cart.gif" /></a>
      <img border="0" src="../images/separator.gif" />

<c:if test="${empty userSession.account}" >
      <a href="<c:url value="/shop/signonForm.do"/>"><img border="0" name="img_signin" src="../images/sign-in.gif" /></a>
</c:if>

<c:if test="${!empty userSession.account}" >
      <a href="<c:url value="/shop/signoff.do"/>"><img border="0" name="img_signout" src="../images/sign-out.gif" /></a>
      <img border="0" src="../images/separator.gif" />
      <a href="<c:url value="/shop/editAccount.do"/>"><img border="0" name="img_myaccount" src="../images/my_account.gif" /></a>
</c:if>

      <img border="0" src="../images/separator.gif" /><a href="../help.html"><img border="0" name="img_help" src="../images/help.gif" /></a>
    </td>
    <td align="left" valign="bottom">
      <form action="<c:url value="/shop/searchProducts.do"/>" method="post">
			  <input type="hidden" name="search" value="true"/>
        <input name="keyword" size="14" />&nbsp;<input border="0" src="../images/search.gif" type="image"/>
      </form>
    </td>
  </tr>
  </tbody>
</table>

<%@ include file="IncludeQuickHeader.jsp" %>
