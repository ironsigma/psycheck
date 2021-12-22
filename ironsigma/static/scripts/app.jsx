'use strict';

function formatCurrency (amount) {
  // convert number to string
  const numString = Math.abs(amount).toString();

  // split whole & decimal numbers
  const decimalIdx = numString.length - 2;
  const wholeNumbers = numString.substring(0, decimalIdx);
  const decimals = numString.substring(decimalIdx);

  // add commas to whole number
  let commaSeparated = "", count = 0;
  const per = 3;

  for (let i = wholeNumbers.length - 1; i >= 0; i--) {
    commaSeparated = wholeNumbers.charAt(i) + commaSeparated;
    if (++count == per && i != 0) {
      commaSeparated = "," + commaSeparated;
      count = 0;
    }
  }

  // return "whole with comma" plus decimal places
  return (amount < 0 ? '-$' : '$') + commaSeparated + "." + decimals;
}

function formatDate(dateStr) {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Sat'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // dateStr is ISO date (i.g. 2021-12-21) since new Date() will parse as UTC
  // we set the time as noon GMT, this will have all time zones in the same day
  const date = new Date(dateStr + "T12:00:00");
  return days[date.getDay()] + ', ' + months[date.getMonth()] + ' ' + date.getDate();
}

function TxComponent(props) {
  const { icon, color, payee, date, memo, amountCents, balanceCents } = props;
  const iconStyle = { color: color };
  const amountStyle = { color: amountCents < 0 ? "#dc3545" : "black" };
  const balanceStyle = { color: balanceCents < 0 ? "#dc3545" : "black" };

  return (
		<div className="row tx-row">
      {/* Icon */}
			<div className="col-sm-1 text-right">
        <i className={"bi-" + icon + " tx-icon"} style={iconStyle}></i>
      </div>

      {/* Paye, Date and Memo */}
			<div className="col-sm">
				<div className="font-weight-bold h4 tx-title">{payee}</div>
				<div className="text-muted">{formatDate(date)}{(memo == null ? '' : [<span> &ndash; </span>, memo])}</div>
      </div>

      {/* Amount */}
			<div className="col-sm-2 text-right font-weight-bold h4 tx-amount" style={amountStyle}>{formatCurrency(amountCents)}</div>

      {/* Balance */}
			<div className="col-sm-2 text-right font-weight-bold h4 tx-amount" style={balanceStyle}>{formatCurrency(balanceCents)}</div>
		</div>
  );
}

class CheckbookComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      items: []
    };
  }

  componentDidMount() {
    $.getJSON("/api/scheduled")
      .done(data => {
        this.setState({
          ...this.state,
          isLoaded: true,
          items: data.transactions
        });
      })
      .fail((_, status, error) => {
        this.setState({
          ...this.state,
          isLoaded: true,
          error: status + ", " + error
        })
      });
  }

  render() {
    const { error, isLoaded, items } = this.state;

    if (error) {
      return <div>Error: {error}</div>;

    } else if (!isLoaded) {
      return <div>Loading...</div>;
    }

    let balanceCents = 100000;
    return (
      <div className="container">
        <div className="row tx-row">
          <div className="col-sm-1">&nbsp;</div>
          <div className="col-sm"><h1>Recent Transactions</h1></div>
        </div>

        {items.map(item => {
            balanceCents += item.amount.fixed;
            return (
              <TxComponent
                key={item.id}
                icon={item.icon}
                color={item.color}
                payee={item.payee}
                date={item.date}
                memo={item.memo}
                amountCents={item.amount.fixed * (item.type === 'credit' ? -1 : 1)}
                balanceCents={balanceCents} />
            );
          }
        )}
      </div>
    );
  }
}

ReactDOM.render(
  <React.StrictMode>
    <CheckbookComponent />
  </React.StrictMode>,
  document.getElementById('app'));
